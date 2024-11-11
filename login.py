import streamlit as st
import mysql.connector
from mysql.connector import Error
import subprocess  # subprocess 추가

# 데이터베이스 연결 함수
def create_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",  # DB 호스트 주소
            user="root",  # DB 사용자 이름
            password="12345678",  # DB 비밀번호
            database="crawled"  # 사용할 데이터베이스 이름
        )
        if connection.is_connected():
            return connection
    except Error as e:
        st.error(f"Error while connecting to MySQL: {e}")
        return None

# 사용자 인증 함수
def authenticate_user(username, password):
    connection = create_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM users WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        return user
    return None

# Streamlit 앱 구성
def main():
    st.markdown("<h1 style='text-align: center; color: #4B7BE5;'>📚 SchoolCatch</h1>", unsafe_allow_html=True)

    st.write("")
    st.write("")
    st.write("")

    col1, col2, col3 = st.columns([1, 3, 1])

    with col2:
        username = st.text_input("아이디", placeholder="아이디를 입력하세요")
        password = st.text_input("비밀번호", type="password", placeholder="비밀번호를 입력하세요")

        if st.button("로그인", help="로그인 버튼을 눌러주세요"):
            user = authenticate_user(username, password)
            if user:
                st.success(f"환영합니다, {user['username']}님!")

                # 로그인 성공 시 chat.py 파일 실행
                subprocess.run(["streamlit", "run", "chat.py"])  # chat.py 실행
            else:
                st.error("잘못된 사용자 이름 또는 비밀번호입니다.")

# main 함수 실행
if __name__ == "__main__":
    main()
