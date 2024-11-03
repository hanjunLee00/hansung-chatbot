#Pinecone DB에서 학습하여 

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, FewShotChatMessagePromptTemplate
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore

from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

from config import answer_examples

store = {}

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
    retriever = database.as_retriever(search_kwargs={'k': 3})
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
def get_llm(model='gpt-4o'):
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
        "물어보는 모든 질문에 대해서는 반드시 한성대 공지 정보를 바탕으로 답변해주세요"
        "모든 질문은 반드시 date 기준으로 최신 정보들을 바탕으로 답변해주세요"
        "공지사항에 대해 알려줄 때에는 Title:, 그리고 date:정보를 빼고 내용과 날짜만 알려주세요"
        "반드시 답변할 때에는 습득한 원본 URL을 링크로 추가하여 답변과 함께 제시해주세요"
        "현재 학기는 24학년도 2학기 입니다. 답변할 때 이를 기준으로 다음학기, 이전학기, 현재학기를 계산해주세요."
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

# 생성된 체인을 바탕으로 ai 답변 생성
def get_ai_response(user_message):
    dictionary_chain = get_dictionary_chain()
    rag_chain = get_rag_chain()
    tax_chain = {"input": dictionary_chain} | rag_chain
    ai_response = tax_chain.stream(
        {
            "question": user_message
        },
        config={
            "configurable": {"session_id": "abc123"}
        },
    )

    return ai_response