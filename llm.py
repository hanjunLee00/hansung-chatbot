import asyncio
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from deep_translator import GoogleTranslator
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from datetime import datetime
import time

from config import answer_examples



# 세션 저장소 및 현재 날짜 설정
store = {}
current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 전역 변수로 캐시 생성
retriever_cache = None
llm_cache = None
dictionary_chain_cache = None

# 로그 및 시간 측정 데코레이터
def log_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"[{func.__name__}] 실행 시간: {elapsed_time:.2f}초")
        return result
    return wrapper

# 세션 히스토리 관리
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

# 임베딩 및 Pinecone 검색 설정
@log_time
def get_retriever():
    global retriever_cache
    if retriever_cache is not None:
        return retriever_cache
    
    embedding = OpenAIEmbeddings(model='text-embedding-3-large')
    index_name = 'crawled-db-ver2'
    database = PineconeVectorStore.from_existing_index(index_name=index_name, embedding=embedding)
    retriever_cache = database.as_retriever(search_kwargs={'k': 3})
    return retriever_cache

# LLM 모델 설정
@log_time
def get_llm(model='gpt-4o-mini'):
    global llm_cache
    if llm_cache is not None:
        return llm_cache

    llm_cache = ChatOpenAI(model=model)
    return llm_cache

# 사전 학습 체인 생성
@log_time
def get_dictionary_chain():
    global dictionary_chain_cache
    if dictionary_chain_cache is not None:
        return dictionary_chain_cache
    
    dictionary = ["학생을 나타내는 표현 -> 부기"]
    llm = get_llm()
    prompt = ChatPromptTemplate.from_template(f"""
        사용자의 질문을 보고, 우리의 사전을 참고해서 사용자의 질문을 변경해주세요.
        사전: {dictionary}
        질문: {{question}}
    """)
    dictionary_chain_cache = prompt | llm | StrOutputParser()
    return dictionary_chain_cache

# 히스토리 인식 검색기 생성
@log_time
def get_history_retriever():
    llm = get_llm()
    retriever = get_retriever()
    
    contextualize_q_system_prompt = (
        "Given a chat history and the latest user question "
        "which might reference context in the chat history, "
        "formulate a standalone question which can be understood "
        "without the chat history. Do NOT answer the question, "
        "just reformulate it if needed and otherwise return it as is"
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

# RAG 체인 생성
@log_time
def get_rag_chain():
    llm = get_llm()
    history_aware_retriever = get_history_retriever()

    # 시스템 프롬프트 설정
    system_prompt = (
        f"오늘 날짜는 {current_date}입니다. "
        "당신의 이름은 상상부기입니다. 학생에게 친근한 말투로, 반말모드로 답변해주세요."
        "모든 질문에 대해 최신 공지사항 정보를 바탕으로 답변합니다. "
        "같은 제목의 공지사항이 여러 개 있다면 최신 정보로 답변합니다. "
        "답변 시 URL 링크를 포함해 주세요."
    )

    # QA 프롬프트 생성 (context 변수 추가)
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
            ("ai", "{context}"),
        ]
    )

    # 문서 결합 체인 생성
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

    # RAG 체인 생성
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    # 대화형 RAG 체인 생성
    conversational_rag_chain = RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    ).pick('answer')

    return conversational_rag_chain

# AI 응답 생성
@log_time
def get_ai_response(user_message, language="한국어"):

    dictionary_chain = get_dictionary_chain()
    rag_chain = get_rag_chain()
    pre_chain = {"input": dictionary_chain} | rag_chain

    ai_response_stream = pre_chain.stream(
        {"question": user_message},
        config={"configurable": {"session_id": "abc123"}}
    )

    if language == "English":
        def translated_stream():
            translator = GoogleTranslator(source="ko", target="en")
            buffer = ""
            for chunk in ai_response_stream:
                buffer += chunk
                if len(buffer) > 100:
                    yield translator.translate(buffer)
                    buffer = ""
            if buffer:
                yield translator.translate(buffer)
        return translated_stream()

    return ai_response_stream