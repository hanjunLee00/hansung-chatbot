import streamlit as st
import mysql.connector
from mysql.connector import Error
import subprocess

if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.set_page_config(page_title="로그인 페이지", layout="wide", initial_sidebar_state="collapsed")
else:
    st.set_page_config(page_title="Chat 페이지", layout="wide", initial_sidebar_state="expanded")


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

# 사용자 중복 확인 함수
def is_username_taken(username):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        return user is not None  # 이미 존재하면 True 반환
    return False

# 사용자 등록 함수
def register_user(username, password, department, student_id):
    if is_username_taken(username):
        st.error("이미 사용 중인 아이디입니다. 다른 아이디를 선택해주세요.")
        return

    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) NOT NULL,
                password VARCHAR(255) NOT NULL,
                department VARCHAR(255),
                student_id VARCHAR(20)
            )
        """)
        cursor.execute("INSERT INTO users (username, password, department, student_id) VALUES (%s, %s, %s, %s)",
                       (username, password, department, student_id))
        connection.commit()
        cursor.close()
        connection.close()
        st.success("회원가입이 완료되었습니다! 로그인 페이지로 이동해주세요.")
    else:
        st.error("데이터베이스 연결에 실패했습니다.")

# 학부 및 학과 데이터
departments = {
    "크리에이티브인문예술대학": ["크리에이티브 인문학부", "예술학부"],
    "미래융합사회과학대학": ["사회과학부"],
    "디자인대학": ["글로벌패션산업학부", "ICT디자인학부", "뷰티디자인매니지먼트학과"],
    "IT공과대학": ["컴퓨터공학부", "기계전자공학부", "IT융합공학부", "산업시스템공학부", "스마트제조혁신컨설팅학과"],
    "창의융합대학": ["상상력인재학부", "문학문화콘텐츠학과", "AI응용학과", "융합보안학과", "미래모빌리티학과"],
    "미래플러스대학": ["융합행정학과", "호텔외식경영학과", "뷰티디자인학과", "비즈니스컨설팅학과", "ICT융합디자인학과", "미래인재학부"]
}

# Streamlit 앱 구성
def main():
    st.markdown("<h1 style='text-align: center; color: #4B7BE5;'>📚 SchoolCatch</h1>", unsafe_allow_html=True)
    st.write("")
    st.write("")
    st.write("")

    col1, col2, col3 = st.columns([1, 3, 1])

    # 회원가입/로그인 전환 변수
    if "register_mode" not in st.session_state:
        st.session_state.register_mode = False

    # 로그인 페이지
    if not st.session_state.register_mode:
        with col2:
            username = st.text_input("아이디", placeholder="아이디를 입력하세요", key="login_username")
            password = st.text_input("비밀번호", type="password", placeholder="비밀번호를 입력하세요", key="login_password")

            if st.button("로그인", help="로그인 버튼을 눌러주세요"):
                user = authenticate_user(username, password)
                if user:
                    st.success(f"환영합니다, {user['username']}님!")
                    st.session_state.logged_in = True
                    st.session_state.user = user
                    st.session_state.department = user['department']  # 부서 정보 저장
                    st.switch_page("./pages/chat.py")  # chat.py 실행
                else:
                    st.error("잘못된 사용자 이름 또는 비밀번호입니다.")

            # 회원가입으로 이동
            if st.button("회원가입하러 가기", help="회원가입 페이지로 이동"):
                st.session_state.register_mode = True
                st.rerun()

    # 회원가입 페이지
    else:
        with col2:
            username = st.text_input("아이디", placeholder="아이디를 입력하세요", key="register_username")
            password = st.text_input("비밀번호", type="password", placeholder="비밀번호를 입력하세요", key="register_password")
            
            # 학부 선택
            main_category = st.selectbox("학부 선택", list(departments.keys()), key="main_category")
            # 학과 선택
            if main_category:
                sub_category = st.selectbox("학과 선택", departments[main_category], key="sub_category")
            else:
                sub_category = ""

            student_id = st.text_input("학번", placeholder="학번을 입력하세요", key="register_student_id")

            if st.button("회원가입", help="회원가입 버튼을 눌러주세요"):
                if username and password and main_category and sub_category and student_id:
                    # 사용자 등록 및 중복 확인
                    register_user(username, password, sub_category, student_id)
                else:
                    st.error("모든 정보를 입력해 주세요.")

            # 로그인 페이지로 돌아가기
            if st.button("로그인 페이지로 돌아가기", help="로그인 페이지로 돌아가기"):
                st.session_state.register_mode = False
                st.rerun()

# main 함수 실행
if __name__ == "__main__":
    main()
