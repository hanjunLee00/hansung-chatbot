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
    st.session_state.theme = "다크 모드"  # Default to dark mode

# Sidebar theme setting with unique key
st.sidebar.subheader("테마 설정")
theme = st.sidebar.radio("테마 선택", ["다크 모드", "라이트 모드"], key="theme_selector")

# Update session state only if the theme changes
if theme != st.session_state.theme:
    st.session_state.theme = theme

# Apply CSS styling based on theme
if st.session_state.theme == "다크 모드":
    st.markdown("""
        <style>
        body { background-color: #000000; color: #f0f0f0; }
        .stApp { background-color: #000000; color: #f0f0f0; }
        h1, h2, h3, h4, h5, h6, p, .faq-title, .stButton>button { color: #f0f0f0; }
        </style>
        """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
        body { background-color: #ffffff; color: #000000; }
        .stApp { background-color: #ffffff; color: #000000; }
        h1, h2, h3, h4, h5, h6, p, .faq-title, .stButton>button { color: #000000; }
        </style>
        """, unsafe_allow_html=True)


# User Guide Toggle
st.sidebar.subheader("사용자 안내서")
if "show_guide" not in st.session_state:
    st.session_state.show_guide = False

if st.sidebar.button("자세히 보기"):
    st.session_state.show_guide = not st.session_state.show_guide  # Toggle visibility

# Display user guide content based on toggle state
if st.session_state.show_guide:
    st.sidebar.markdown("""
    - **질문을 간결하게 작성하세요**: 명확하고 짧은 질문이 더 정확한 답변을 제공합니다.
    - **한성대 관련 정보만 제공**: 학업, 캠퍼스, 장학금 등 한성대 관련 정보에 집중되어 있습니다.
    """)

# Main content and other code remains the same
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

# Initialize session state to store messages
if 'message_list' not in st.session_state:
    st.session_state.message_list = []

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&family=Montserrat:wght@400;700&display=swap');

    /* 기본 설정 */
    body {
        font-family: 'Roboto', sans-serif;
        color: #f0f0f0;
        background-color: #2b2b2b;  /* 어두운 배경 */
    }

    /* FAQ 섹션 스타일 */
    .faq-section {
        background-color: #333333;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.5);
        margin-bottom: 20px;
    }
    
    .faq-title {
        font-family: 'Montserrat', sans-serif;
        font-size: 1.3em;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 15px;
        text-align: center;
    }
    
    /* 버튼 스타일 및 애니메이션 */
    .stButton>button {
        font-family: 'Roboto', sans-serif;
        width: 100%;
        padding: 12px;
        border-radius: 8px;
        background-color: #444444;
        color: #e0e0e0;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.4);
        border: 1px solid #555555;
        transition: background-color 0.3s, box-shadow 0.3s, transform 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #555555;
        box-shadow: 0 4px 8px rgba(255, 255, 255, 0.2);
        transform: scale(1.05);
    }
    
    /* 채팅 메시지 스타일 */
    .chat-message-user {
        background-color: #3a3a3a;
        color: #ffffff;
        padding: 12px 18px;
        border-radius: 10px;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .chat-message-bot {
        background-color: #4b4b4b;
        color: #e0e0e0;
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

# Sticky FAQ section with buttons
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

# Display past messages
for message in st.session_state.message_list:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.write(message["content"])
    elif message["role"] == "ai":
        with st.chat_message("ai"):
            st.write(message["content"])

# Chat input for custom questions
if user_question := st.chat_input(placeholder="한성대에 관련된 궁금한 내용들을 말씀해주세요!"):
    # Display user question in chat
    with st.chat_message("user"):
        st.write(user_question)
    st.session_state.message_list.append({"role": "user", "content": user_question})

    # Generate AI response
    with st.spinner("답변을 생성하는 중입니다..."):
        ai_response = get_ai_response(user_question)
        with st.chat_message("ai"):
            ai_message = st.write_stream(ai_response)
        st.session_state.message_list.append({"role": "ai", "content": ai_message})