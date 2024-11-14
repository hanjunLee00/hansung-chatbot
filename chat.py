#학습된 llm으로 채팅 화면 구성

from dotenv import load_dotenv
import streamlit as st
from llm import get_ai_response

st.set_page_config(page_title="한성대 챗봇", page_icon="🤖")

st.title("🤖 한성대 챗봇")
st.caption("한성대에 관련된 모든것을 답해드립니다!")

load_dotenv()

if 'message_list' not in st.session_state:
    st.session_state.message_list = []

for message in st.session_state.message_list:
    with st.chat_message(message["role"]):
        st.write(message["content"])

#자주 묻는 질문 등 간단한 UI 추가할 부분

# 유저 메세지를 입력받고 ai 답변을 받아와 출력
if user_question := st.chat_input(placeholder="한성대에 관련된 궁금한 내용들을 말씀해주세요!"):
    with st.chat_message("user"):
        st.write(user_question)
    st.session_state.message_list.append({"role": "user", "content": user_question})

    with st.spinner("답변을 생성하는 중입니다"):
        ai_response = get_ai_response(user_question)
        with st.chat_message("ai"):
            ai_message = st.write_stream(ai_response)
            st.session_state.message_list.append({"role": "ai", "content": ai_message})
            