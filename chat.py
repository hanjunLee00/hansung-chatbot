#ui 전용
from llm import get_ai_response
import streamlit as st
from dotenv import load_dotenv


st.set_page_config(page_title="한성대 챗봇", page_icon="🤖")
st.title("🤖 스쿨캐치")
st.caption("한성대에 관련된 모든것을 답해드립니다!")

load_dotenv()

# Initialization               
if 'message_list' not in st.session_state:
    st.session_state.message_list = []

 # 세션 내에 이전 채팅 기록들을 st.session_state.message_list에 기록
# print(f"before == {st.session_state.message_list}")

# 반복문 : 이전에 있었던 채팅 내용들을 화면에 그림
for message in st.session_state.message_list:
    with st.chat_message(message["role"]):
        st.write(message["content"])



#사용자가 채팅을 입력할 때 마다 실행됨
if user_question := st.chat_input(placeholder="한성대에 관련된 궁금한 내용들을 말씀해주세요!"):
    with st.chat_message("user"):
        st.write(user_question)
    st.session_state.message_list.append({"role" : "user", "content" : user_question})

    with st.spinner("답변을 생성하는 중입니다"):
        ai_message = get_ai_response(user_question)
        with st.chat_message("ai"):
            st.write(ai_message)
        st.session_state.message_list.append({"role" : "ai", "content" : ai_message})
# 채팅 후에는 방금 입력된 채팅을 포함하여 기록
# print(f"after == {st.session_state.message_list}")



#한 세션 안에서 채팅 기록들을 저장해두는 전역변수와 비슷한 개념 => Session State
