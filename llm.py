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
from datetime import datetime, timedelta
import re
from config import answer_examples

# 세션 저장소 및 현재 날짜 설정
store = {}
current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# 세션 히스토리 관리
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

# 타임스탬프 값을 보기쉽게 변환함
def format_timestamp_to_date(timestamp):
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

# 사용자의 질문 중 날짜 표현이 있으면 Metadata 기반 Filter 생성
def get_date_filter(user_message):
    today = datetime.now()
    
    # '오늘' 처리
    if "오늘" in user_message:
        start_of_day = today.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1) - timedelta(seconds=1)
        date_filter = {"expiry_date": {"$gte": int(start_of_day.timestamp()), "$lte": int(end_of_day.timestamp())}}
        print(f"\n오늘 표현 필터 : {date_filter}")
        print(f"오늘 시작 : {format_timestamp_to_date(int(start_of_day.timestamp()))}, "
              f"오늘 종료 : {format_timestamp_to_date(int(end_of_day.timestamp()))}")
        return date_filter
    
    # '어제' 처리
    elif "어제" in user_message:
        start_of_yesterday = (today - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_yesterday = start_of_yesterday + timedelta(days=1) - timedelta(seconds=1)
        date_filter = {"expiry_date": {"$gte": int(start_of_yesterday.timestamp()), "$lte": int(end_of_yesterday.timestamp())}}
        print(f"\n어제 표현 필터 : {date_filter}")
        print(f"어제 시작 : {format_timestamp_to_date(int(start_of_yesterday.timestamp()))}, "
              f"어제 종료 : {format_timestamp_to_date(int(end_of_yesterday.timestamp()))}")
        return date_filter
    
    # '이번 주' 처리
    elif "이번 주" in user_message:
        start_of_week = today - timedelta(days=today.weekday())
        start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_week = start_of_week + timedelta(days=7) - timedelta(seconds=1)
        date_filter = {"expiry_date": {"$gte": int(start_of_week.timestamp()), "$lte": int(end_of_week.timestamp())}}
        print(f"\n이번 주 필터 : {date_filter}")
        print(f"이번 주 시작 : {format_timestamp_to_date(int(start_of_week.timestamp()))}, "
              f"이번 주 종료 : {format_timestamp_to_date(int(end_of_week.timestamp()))}")
        return date_filter
    
    # '최신' 또는 '최근' 처리
    elif "최신" in user_message or "최근" in user_message:
        start_date = today - timedelta(days=7)
        date_filter = {"expiry_date": {"$gte": int(start_date.timestamp())}}
        print(f"\n최근 필터 : {date_filter}")
        print(f"최근 시작 : {format_timestamp_to_date(int(start_date.timestamp()))}")
        return date_filter
    
    # 날짜 형식 (YYYY-MM-DD) 처리
    elif match := re.search(r"(\d{4})[년\s]?(\d{1,2})[월\s]?(\d{1,2})[일\s]?", user_message):
        # 사용자가 년, 월, 일을 다양한 방식으로 입력할 수 있도록 처리
        year = int(match.group(1))
        month = int(match.group(2))
        day = int(match.group(3))
        
        try:
            specific_date = datetime(year, month, day)
            start_of_day = specific_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = start_of_day + timedelta(days=1) - timedelta(seconds=1)
            date_filter = {"expiry_date": {"$gte": int(start_of_day.timestamp()), "$lte": int(end_of_day.timestamp())}}
            
            print(f"\n날짜 지정 필터 : {date_filter}")
            print(f"날짜 지정 시작 : {format_timestamp_to_date(int(start_of_day.timestamp()))}, "
                  f"날짜 지정 종료 : {format_timestamp_to_date(int(end_of_day.timestamp()))}\n")
            return date_filter
        except ValueError:
            print(f"날짜 표현이 잘못된 것 같아! 정확한 날짜를 입력해줘!! (예시: 11월 28일, 2024년 11월 28일 등): {user_message}\n")
            return None
    
    return None

# 임베딩 및 Pinecone 검색 설정
def get_retriever(user_message):
    
    embedding = OpenAIEmbeddings(model='text-embedding-3-large')
    index_name = 'crawled-db-ver2'
    database = PineconeVectorStore.from_existing_index(index_name=index_name, embedding=embedding)

    # 날짜 필터 적용
    date_filter = get_date_filter(user_message)
    search_kwargs = {"k": 5}  # 기본 검색 설정
    if date_filter:
        search_kwargs["filter"] = date_filter  # 날짜 필터 추가
    
    retriever_cache = database.as_retriever(search_kwargs=search_kwargs)
    return retriever_cache

# LLM 모델 설정
def get_llm(model='gpt-4o-mini'):

    llm_cache = ChatOpenAI(model=model)
    return llm_cache

# 히스토리 인식 검색기 생성
def get_history_retriever(user_message):
    llm = get_llm()
    retriever = get_retriever(user_message)
    
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
def get_rag_chain(user_message):
    llm = get_llm()
    history_aware_retriever = get_history_retriever(user_message)

    # 시스템 프롬프트 설정
    system_prompt = (
        f"오늘 날짜는 {current_date}입니다. "
        "유저가 물어보지 않았는데 마음대로 최신 공지사항, 추천 공지사항과 같은 정보를 알려주지 마세요"
        "당신의 이름은 상상부기입니다. 학생에게 친근한 말투로, 반말모드로 답변해주세요."
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
def get_ai_response(user_message, language="한국어"):

    rag_chain = get_rag_chain(user_message)

    ai_response_stream = rag_chain.stream(
        {"input": user_message},
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
