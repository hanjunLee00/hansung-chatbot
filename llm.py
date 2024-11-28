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
import re, time
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

def get_date_filter(user_message):
    today = datetime.now()
    current_year = today.year
    current_month = today.month

    # 정규식: "11월 25일", "25일" 같은 표현을 포착
    match = re.search(r"(?:(\d{4})[년\s\-\.]?)?\s*(?:(\d{1,2})[월\s\-\.]?)?\s*(\d{1,2})[일]?", user_message)
    
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

    # 정규식: "11월 25일", "25일" 같은 표현을 정확히 매칭
    match = re.search(r"(?:(\d{4})[년\s\-\.]?)?\s*(?:(\d{1,2})[월\s\-\.]?)?\s*(\d{1,2})[일]?", user_message)

    if match:
        try:
            # 연도, 월, 일 추출 및 기본값 설정
            year = int(match.group(1)) if match.group(1) else current_year
            month = int(match.group(2)) if match.group(2) else current_month
            day = int(match.group(3))

            # 날짜 유효성 검사 및 처리
            specific_date = datetime(year, month, day)

            # 타임스탬프 계산
            start_of_day = specific_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = start_of_day + timedelta(days=1) - timedelta(seconds=1)

            date_filter = {
                "expiry_date": {
                    "$gte": int(start_of_day.timestamp()),
                    "$lte": int(end_of_day.timestamp())
                }
            }
            print(f"\n사용자 입력 날짜: {specific_date.strftime('%Y-%m-%d')}")
            print(f"날짜 지정 필터: {date_filter}")
            return date_filter

        except ValueError:
            print("날짜 계산 중 오류 발생: 유효하지 않은 날짜입니다.")
            
    # 이외의 질문 처리: 기본적으로 "" 필터 사용
    elif "최근" in user_message or "최신" in user_message:
        start_date = today - timedelta(days=7)
        date_filter = {"expiry_date": {"$gte": int(start_date.timestamp())}}
        print(f"\n최근 공지 필터 : {date_filter}")
        return date_filter
    
    elif "이번 주" in user_message or "이번주" in user_message:
        # 이번 주의 시작일 (일요일)
        start_of_week = today - timedelta(days=today.weekday() + 1)  # 일요일로 이동
        start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)

        # 이번 주의 끝일 (토요일)
        end_of_week = start_of_week + timedelta(days=6) + timedelta(hours=23, minutes=59, seconds=59)

        date_filter = {"expiry_date": {"$gte": int(start_of_week.timestamp()), "$lte": int(end_of_week.timestamp())}}
        print(f"\n이번 주 표현 필터 : {date_filter}")
        print(f"이번 주 시작 : {format_timestamp_to_date(int(start_of_week.timestamp()))}, "
              f"이번 주 종료 : {format_timestamp_to_date(int(end_of_week.timestamp()))}")
        return date_filter

# 임베딩 및 Pinecone 검색 설정
def get_retriever(user_message):
    
    embedding = OpenAIEmbeddings(model='text-embedding-3-large')
    index_name = 'crawled-db-ver2'
    database = PineconeVectorStore.from_existing_index(index_name=index_name, embedding=embedding)

    # 날짜 필터 적용
    date_filter = get_date_filter(user_message)
    search_kwargs = {"k": 3}  # 기본 검색 설정
    if date_filter:
        search_kwargs["filter"] = date_filter  # 날짜 필터 추가
    
    retriever = database.as_retriever(search_kwargs=search_kwargs)
    return retriever

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
        "당신의 이름은 상상부기이고, 학생들에게 한성대학교 공지사항을 요약해주는 챗봇입니다. 학생에게 친근한 말투로, 반말모드로 답변해주세요."
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
