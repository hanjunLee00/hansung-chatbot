from dotenv import load_dotenv
import streamlit as st
from llm import get_ai_response
from PIL import Image

icon_image = Image.open("./hansungbu.png")

# 사용자 지정 아이콘으로 페이지 구성 설정
st.set_page_config(page_title="한성대학교 챗봇", page_icon=icon_image)

# 언어 선택 기능 추가
st.sidebar.title("언어 선택 / Language Selection")
language = st.sidebar.radio("Choose Language", ('한국어', 'English'))

if 'theme' not in st.session_state:
    st.session_state.theme = "라이트 모드"  # 기본값을 라이트 모드로 설정

# Sidebar 테마 설정
st.sidebar.subheader("테마 설정")
theme = st.sidebar.radio("테마 선택", ["다크 모드", "라이트 모드"], key="theme_selector")

# 테마가 변경되면 session_state에 반영
if theme != st.session_state.theme:
    st.session_state.theme = theme

# 테마에 맞는 CSS 스타일 적용
if st.session_state.theme == "다크 모드":
    st.markdown("""
        <style>
            
            body {
                background-color: #0f0f0f;  /* 다크 모드 배경 */
                color: white !important;
            }
            .stApp { 
                background-color: #0f0f0f;
            }
             h1 {
                color: #ffffff !important;
            }
            .stButton>button {
                background-color: #333;  /* 다크 모드 버튼 배경 */
                color: white;  /* 다크 모드 버튼 텍스트 */
            }
            .stSidebar {/* 다크 모드 사이드바 배경 및 중간크기 글씨 색*/
                background-color : #212121;
                color : white;
            }
            .st-bs { /* 라디오바 글자색 */
                color : #9f9f9f;
            }
            .st-emotion-cache-ue6h4q{ /* 라디오바 위 설명란 글자색 */
                color : #b1b1b1;
            }
            .st-emotion-cache-128upt6 { /* 메인 하단 색상 */
                background-color : #0f0f0f;
            }
            .st-emotion-cache-12fmjuu{ /* 메인 상단 색상 */
                background-color : #0f0f0f;
                color : white;
            }
            .st-emotion-cache-uuorpk {
                color : #b1b1b1;
            }
            .faq-section {
                background-color: #1c1c1c;
            }
            .faq-title {
                font-size: 18px;
                color: #f5f5f5;
                padding: 10px;
            }
            .stButton>button:hover { /* 버튼들 호버색*/
                background-color: #555555;
            }
            .st-emotion-cache-1c7y2kd { /* 질문자 메시지 스타일 */
                background-color : #7a7a7a;
            }
            .st-emotion-cache-4oy321{ /* 답변자 메세지 스타일 */
                background-color : #444444;
            }
            .st-emotion-cache-1flajlm{ /* 질답 글자색 */
                color : white;
            }
            .st-ct { /* 텍스트창 */
                background-color: #444444;
            }
            .st-ct::placeholder {
                color : #9c9c9c;
            }
        </style>
    """, unsafe_allow_html=True)
else:  # 라이트 모드
    st.markdown("""
        <style>
            body {
                background-color: #ffffff;  /* 라이트 모드 배경 */
                color: #000000 !important;
            }
            .stButton>button {
                background-color: #f0f0f0;  /* 라이트 모드 버튼 배경 */
                color: black;  /* 라이트 모드 버튼 텍스트 */
            }
            .stButton>button:hover { /* 버튼들 호버색*/
                background-color: white;
            }
            .faq-section {
                background-color: #f9f9f9;
            }
            .faq-title {
                font-size: 18px;
                color: #333;
                padding: 10px;
            }
            .st-emotion-cache-1c7y2kd { /* 질문자 메시지 스타일 */
                background-color : #f9f9f9;
            }
        </style>
    """, unsafe_allow_html=True)
# 사용자 안내서 토글
st.sidebar.subheader("사용자 안내서")
if "show_guide" not in st.session_state:
    st.session_state.show_guide = False

if st.sidebar.button("자세히 보기"):
    st.session_state.show_guide = not st.session_state.show_guide  # 가시성 전환

# 사용자 안내서 내용 표시
if st.session_state.show_guide:
    st.sidebar.markdown("""
    - **질문을 간결하게 작성하세요**: 명확하고 짧은 질문이 더 정확한 답변을 제공합니다.
    - **한성대 관련 정보만 제공**: 학업, 캠퍼스, 장학금 등 한성대 관련 정보에 집중되어 있습니다.
    """)

# 피드백 섹션
st.sidebar.subheader("피드백")
feedback = st.sidebar.text_area("챗봇에 대한 의견을 작성해주세요.")
if st.sidebar.button("피드백 제출"):
    st.success("피드백이 제출되었습니다. 감사합니다!")

title_icon = Image.open("./hansungbu.png")

# 언어에 따라 타이틀과 캡션을 설정
if language == '한국어':
    title_text = "한성대학교 챗봇"
    caption = "한성대에 관련된 모든 것을 답해드립니다!"
else:
    title_text = "Hansung University Chatbot"
    caption = "Get answers to everything related to Hansung University!"

# 이미지와 텍스트 타이틀을 순서대로 표시
st.image(title_icon, width=200)  # 이미지 크기는 필요에 따라 조절
st.title(title_text)
st.caption(caption)

load_dotenv()

# 메시지 목록 초기화
if 'message_list' not in st.session_state:
    st.session_state.message_list = []

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&family=Montserrat:wght@400;700&display=swap');
    /* 기본 설정 */
    body {
        font-family: 'Roboto', sans-serif;
    }

    /* FAQ 섹션 스타일 */
    .faq-section {
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.5);
        margin-bottom: 20px;
    }
    
    .faq-title {
        font-family: 'Montserrat', sans-serif;
        font-size: 1.3em;
        font-weight: 700;
        margin-bottom: 15px;
        text-align: center;
    }
    
    /* 버튼 스타일 및 애니메이션 */
    .stButton>button {
        font-family: 'Roboto', sans-serif;
        width: 100%;
        padding: 12px;
        border-radius: 8px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.4);
        border: 1px solid #555555;
        transition: background-color 0.3s, box-shadow 0.3s, transform 0.3s ease;
    }
    
    .stButton>button:hover {
        box-shadow: 0 4px 8px rgba(255, 255, 255, 0.2);
        transform: scale(1.05);
    }
    
    /* 채팅 메시지 스타일 */
    .stChatMessage{
        padding: 12px 18px;
        border-radius: 10px;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }

    /* 반응형 디자인 */
    @media (max-width: 768px) {
        .faq-section {
            padding: 10px;
            margin-bottom: 10px;
        }
        
        .faq-title {
            font-size: 1.1em;
        }
        
        .stButton>button {
            padding: 10px;
            font-size: 0.9em;
        }
    }

    </style>
""", unsafe_allow_html=True)

# FAQ 섹션 (고정)
with st.container():
    st.markdown('<div class="faq-section">', unsafe_allow_html=True)
    st.markdown('<div class="faq-title">📌 자주 질문하는 정보</div>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)

    # FAQ 버튼 텍스트와 질문을 선택된 언어에 맞게 표시
    faq_options = {
        '한국어': ["🎓 장학금", "🗺️ 캠퍼스맵", "💰 등록금", "📝 시험일정"],
        'English': ["🎓 Scholarships", "🗺️ Campus Map", "💰 Tuition", "📝 Exam Schedule"]
    }
    faq_questions = {
        '한국어': ["2024학년도 2학기 교내 장학금에 대한 종류 알려주세요", "캠퍼스맵에 대한 정보", "2024 학년도 2학기 등록금에 대한 정보 알려주세요", "2024 학년도 2학기 시험일정에 대한 정보"],
        'English': ["Information about scholarships", "Information about the campus map", "Information about tuition", "Information about the exam schedule"]
    }

    for i, (button_text, question) in enumerate(zip(faq_options[language], faq_questions[language])):
        with [col1, col2, col3, col4][i]:
            if st.button(button_text):
                st.session_state.message_list.append({"role": "user", "content": question})
                # 선택된 언어에 따라 답변 생성
                ai_response = get_ai_response(question)  # 언어 인자 없이 호출
                st.session_state.message_list.append({"role": "ai", "content": ai_response})
    st.markdown('</div>', unsafe_allow_html=True)

# 이전 메시지들 표시
for message in st.session_state.message_list:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.write(message["content"])
    elif message["role"] == "ai":
        with st.chat_message("ai"):
            st.write(message["content"])

# 사용자 질문 입력
if user_question := st.chat_input(placeholder="한성대에 관련된 궁금한 내용들을 말씀해주세요!"):
    # 사용자 질문을 채팅에 표시
    with st.chat_message("user"):
        st.write(user_question)
    st.session_state.message_list.append({"role": "user", "content": user_question})

    # AI 답변 생성
    with st.spinner("답변을 생성하는 중입니다..."):
        ai_response = get_ai_response(user_question)
        with st.chat_message("ai"):
            ai_message = st.write_stream(ai_response)
        st.session_state.message_list.append({"role": "ai", "content": ai_message})
