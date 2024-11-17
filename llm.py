from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, FewShotChatMessagePromptTemplate
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from deep_translator import GoogleTranslator
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
import datetime
from datetime import datetime

from config import answer_examples

store = {}

current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 이전 채팅 기록들 유지
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

# 임베딩 모델 설정하여 PineCone DB에서 정보 검색 (임계값 k = 3)
def get_retriever():
    embedding = OpenAIEmbeddings(model='text-embedding-3-large')
    index_name = 'crawled-db-ver2'
    database = PineconeVectorStore.from_existing_index(index_name=index_name, embedding=embedding)
    retriever = database.as_retriever(search_kwargs={'k': 10})
    return retriever

# llm, retriever 
def get_history_retriever():
    llm = get_llm()
    retriever = get_retriever()
    
    contextualize_q_system_prompt = (
        "Given a chat history and the latest user question "
        "which might reference context in the chat history, "
        "formulate a standalone question which can be understood "
        "without the chat history. Do NOT answer the question, "
        "just reformulate it if needed and otherwise return it as is."
    )

    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    
    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
    )
    return history_aware_retriever

#llm 모델 선정
def get_llm(model='gpt-4o-mini'):
    llm = ChatOpenAI(model=model)
    return llm

#사전 학습 데이터 설정 (수정 필요)
def get_dictionary_chain():
    dictionary = ["사람을 나타내는 표현 -> 학생"]
    llm = get_llm()
    prompt = ChatPromptTemplate.from_template(f"""
        사용자의 질문을 보고, 우리의 사전을 참고해서 사용자의 질문을 변경해주세요.
        만약 변경할 필요가 없다고 판단된다면, 사용자의 질문을 변경하지 않아도 됩니다.
        그런 경우에는 질문만 리턴해주세요
        사전: {dictionary}
        질문: {{question}}
    """)

    dictionary_chain = prompt | llm | StrOutputParser()
    
    return dictionary_chain

# RAG 채인 생성
def get_rag_chain():
    llm = get_llm()
    example_prompt = ChatPromptTemplate.from_messages(
        [
            ("human", "{input}"),
            ("ai", "{answer}"),
        ]
    )
    few_shot_prompt = FewShotChatMessagePromptTemplate(
        example_prompt=example_prompt,
        examples=answer_examples,
    )
    system_prompt = (
        f"오늘 날짜는 {current_date} 입니다."
        "물어보는 모든 질문에 대해서는 반드시 한성대 공지 정보를 바탕으로 답변해주세요"
        "모든 질문은 반드시 Date 기준으로 최신 정보들을 바탕으로 답변해주세요"
        "같은 제목의 공지사항이 여러개 있으면 가장 최신 정보를 바탕으로 답변해주세요"
        "공지사항에 대해 알려줄 때에는 Title:, 그리고 date:정보를 빼고 내용과 날짜만 알려주세요"
        "반드시 답변할 때에는 습득한 원본 URL을 링크로 추가하여 답변과 함께 제시해주세요"
        "현재 학기는 24학년도 2학기 입니다. 모든 질문은 반드시 Date 기준으로 최신 정보들을 바탕으로 답변해주세요. 답변할 때 이를 기준으로 다음학기, 이전학기, 현재학기를 계산해주세요."
        "참고로 다음학기는 25학년도 1학기, 이전 학기는 24학년도 1학기입니다."
        "이번 방학은 2학기 종강 이후 있을 겨울 방학입니다."
        "\n\n"
        "{context}"
    )

    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            few_shot_prompt,
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    history_aware_retriever = get_history_retriever()
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
    
    conversational_rag_chain = RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    ).pick('answer')
    
    return conversational_rag_chain

# Pinecone에서 검색 후 정렬하는 함수 추가
def sort_results_by_date(results):
    # 메타데이터에서 날짜를 추출하여 정렬
    def parse_date(result):
        date_str = result.metadata.get('date', '')
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return datetime.min  # 날짜가 잘못되었거나 없는 경우 최소 날짜로 설정
    return sorted(results, key=parse_date, reverse=True)

# 최신 공지사항을 가져오는 함수
def get_latest_notice():
    retriever = get_retriever()
    results = retriever.get_relevant_documents("가장 최근 공지")
    
    # 날짜 기준으로 정렬하여 최신 공지사항 가져오기
    sorted_results = sort_results_by_date(results)
    
    if sorted_results:
        latest_notice = sorted_results[0]
        content = latest_notice.page_content
        date = latest_notice.metadata.get('date', '날짜 정보 없음')
        return f"가장 최근 공지사항은 다음과 같습니다.\n\n내용: {content}\n\n날짜: {date}"
    else:
        return "최근 공지사항을 찾을 수 없습니다."

# 생성된 체인을 바탕으로 ai 답변 생성 (제너레이터 형태 유지)
def get_ai_response(user_message, language="한국어"):
    if "가장 최근 공지사항" in user_message or "최근 공지" in user_message:
        return get_latest_notice()
    
    # Dictionary Chain과 RAG Chain 생성
    dictionary_chain = get_dictionary_chain()
    rag_chain = get_rag_chain()
    tax_chain = {"input": dictionary_chain} | rag_chain

    # 제너레이터 형태의 응답 생성
    ai_response_stream = tax_chain.stream(
        {
            "question": user_message
        },
        config={
            "configurable": {"session_id": "abc123"}  # 세션 ID 관리
        },
    )

    # 언어가 영어라면 번역된 제너레이터 반환
    if language == "English":
        def translated_stream():
            translator = GoogleTranslator(source="ko", target="en")
            buffer = ""  # 텍스트 버퍼
            for chunk in ai_response_stream:
                buffer += chunk  # 버퍼에 데이터 추가
                if len(buffer) > 100:  # 버퍼가 충분히 채워지면 번역
                    translated = translator.translate(buffer)
                    yield translated  # 번역된 데이터를 반환
                    buffer = ""  # 버퍼 초기화
            if buffer:  # 남아있는 텍스트 처리
                yield translator.translate(buffer)

        return translated_stream()  # 영어일 경우 번역된 스트림 반환

    return ai_response_stream 