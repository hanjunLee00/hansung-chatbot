from dotenv import load_dotenv
import streamlit as st
from llm import get_ai_response
from PIL import Image
from datetime import datetime
import mysql.connector  # 공지사항 관리를 위한 데이터베이스 사용

# MySQL 연결 설정
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="12345678",
    database="crawled"
)
cursor = db.cursor()

def get_recent_notices(limit=3):
    cursor.execute("SELECT title, link, date FROM swpre ORDER BY date DESC LIMIT %s", (limit,))
    return cursor.fetchall() 

icon_image = Image.open("./image/hansungbu.png")

# 사용자 지정 아이콘으로 페이지 구성 설정
st.set_page_config(page_title="한성대학교 챗봇", page_icon=icon_image)

# 탭기능 - 언어선택

st.sidebar.title("언어 선택 / Language Selection")
language = st.sidebar.radio("　", ('한국어', 'English'))
# 구분선 추가
st.sidebar.markdown(
    """
    <hr style="
        border: none;
        height: 2px;
        background-color: #cccccc;
        margin: 15px 0;
    ">
    """,
    unsafe_allow_html=True
)

# 테마 기본값 설정
if 'theme' not in st.session_state:
    st.session_state.theme = "라이트 모드"  # 기본값은 라이트 모드

# Sidebar 테마 설정
st.sidebar.subheader("테마 설정" if language == '한국어' else "Theme Settings")
theme = st.sidebar.radio(
    "　" if language == '한국어' else "　",
    ["라이트 모드", "다크 모드"] if language == '한국어' else ["Light Mode", "Dark Mode"],
    index=0  # 기본 선택값을 "라이트 모드"로 설정
)

# 테마가 변경되면 session_state에 반영
if theme != st.session_state.theme:
    st.session_state.theme = theme
    

# 테마에 맞는 CSS 스타일 적용
if st.session_state.theme in ["다크 모드", "Dark Mode"]:
    st.markdown("""
        <style>
            
            body {
                background-color: #0f0f0f;  /* 다크 모드 배경 */
                color: white !important;
            }
            .stApp { 
                background-color: #0f0f0f;
            }
             h1, h3, h5{
                color: white !important;
            }
            .custom-caption {
                color : #b1b1b1;
                font-size : 0.8rem;
            }
            .stButton>button {
                background-color: #333;  /* 다크 모드 버튼 배경 */
                color: white;  /* 다크 모드 버튼 텍스트 */
            }
            .stSidebar {/* 다크 모드 사이드바 배경 및 중간크기 글씨 색*/
                background-color : #212121;
                color : white;
            }
            .st-bc { /* 라디오바 글자색 */
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
            .faq-section {
                background-color: #1c1c1c;
            }
            .faq-title {
                font-size: 18px;
                color: #f5f5f5;
                padding: 10px;
            }
            .faq-content {
                background-color : #222222;
                color: #ffffff;
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
            .stChatInput { /* 택스트창 */
                background-color : #bdbdbd;
            }
            .notice-item {
                background-color : #333;
                color : white;
            }
            .recent_notice {
                background-color : #333;
                color : white;
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
            .notice-item {
                background-color : #f9f9f9;
            }
        </style>
    """, unsafe_allow_html=True)
    # 구분선 추가
st.sidebar.markdown(
    """
    <hr style="
        border: none;
        height: 2px;
        background-color: #cccccc;
        margin: 15px 0;
    ">
    """,
    unsafe_allow_html=True
)

# 탭기능 - 사용자 안내서
st.sidebar.subheader("사용자 안내서" if language == '한국어' else "User Guide")
if "show_guide" not in st.session_state:
    st.session_state.show_guide = False

if st.sidebar.button("자세히 보기" if language == '한국어' else "View Details"):
    st.session_state.show_guide = not st.session_state.show_guide  

if st.session_state.show_guide:
    if language == '한국어':
        st.sidebar.markdown("""
        - **구체적인 정보를 받아보세요!**:   
                            ex) **계절학기 시작 날짜**가 언제야?  
                            ex) **프로그래밍 캠프 날짜**가 언제야?  
        - **날짜 기반으로 검색해보세요!**:   
                            ex) **어제** 올라온 공지 알려줘!  
                            ex) **오늘** 올라온 공지 있어?  
                            ex) **11월 25일** 올라온 공지 있어? 
                                (월/일 필수입력!)  
        - **한성대 관련 정보만 제공**:  
                            학업, 캠퍼스, 장학금 등 **한성대 관련 정보**에 집중되어 있습니다.  
        """)
    else:
        st.sidebar.markdown("""
        - **Get specific information!**:  
                            ex) When does the **seasonal semester start**?  
                            ex) What's the date for the **programming camp**?  
        - **Search based on dates!**:  
                            ex) Show me notices posted **yesterday**.  
                            ex) Are there any notices posted **today**?  
                            ex) Are there any notices posted on **November 25th**?  
                                (Month/Day required!)  
        - **Providing information exclusively about Hansung University**:  
                            Focused on topics such as academics, campus life, scholarships, and other **Hansung University-related information**.  
        """)
# 구분선 추가
st.sidebar.markdown(
    """
    <hr style="
        border: none;
        height: 2px;
        background-color: #cccccc;
        margin: 15px 0;
    ">
    """,
    unsafe_allow_html=True
)

# 탭기능 - 에브리타임 바로가기
st.sidebar.subheader(
    "한성대학교 에브리타임 바로가기" if language == '한국어' else "Hansung University Everytime Shortcut"
)

st.sidebar.markdown(
    f"""
    <a href="https://hansung.everytime.kr/" target="_blank" style="
        display: block;
        background-color: #28a745;
        color: white;
        text-align: center;
        text-decoration: none;
        padding: 12px 20px;
        margin-top: 10px;
        margin-bottom: 10px;
        border-radius: 8px;
        font-size: 16px;
        font-weight: bold;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
        transition: background-color 0.3s ease;
    " onmouseover="this.style.backgroundColor='#218838'" onmouseout="this.style.backgroundColor='#28a745'">
        {'한성대학교 에브리타임' if language == '한국어' else 'Hansung University Everytime'}
    </a>
    """,
    unsafe_allow_html=True
)

# 한성대학교 홈페이지 바로가기 버튼
st.sidebar.subheader(
    "한성대학교 홈페이지 바로가기" if language == '한국어' else "Hansung University Website Shortcut"
)

st.sidebar.markdown(f"""
    <a href="https://www.hansung.ac.kr/sites/hansung/index.do" target="_blank" style="
        display: block;
        background-color: #007BFF;
        color: white;
        text-align: center;
        text-decoration: none;
        padding: 12px 20px;
        margin-top: 10px;
        margin-bottom: 10px;
        border-radius: 8px;
        font-size: 16px;
        font-weight: bold;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
        transition: background-color 0.3s ease;
    " onmouseover="this.style.backgroundColor='#0056b3'" onmouseout="this.style.backgroundColor='#007BFF'">
        {'한성대학교 홈페이지' if language == '한국어' else 'Hansung University Website'}
    </a>
""", unsafe_allow_html=True)

title_icon = Image.open("./hansungbu.png")

# 언어에 따라 타이틀과 캡션을 설정
if language == '한국어':
    title_text = "한성대학교 챗봇"
    caption = "안녕 난 상상부기! 뭐든 물어봐!"
else:
    title_text = "School Catch"
    caption = "Get answers to everything related to Hansung University!"

    
# 챗봇 이미지와 최근공지사항 버튼 
with st.container():
    col1, col2 = st.columns([1, 1])  

    # 왼쪽 컬럼에 이미지와 타이틀 표시
    with col1:
        st.image(title_icon, width=200)  
        st.title(title_text)
        st.markdown(f'<p class="custom-caption">{caption}</p>', unsafe_allow_html=True)

with col2:
    if "show_recent_notices" not in st.session_state:
        st.session_state.show_recent_notices = False

    button_text = "📢 최근 공지사항 보기" if language == '한국어' else "📢 View Recent Notices"
    
    if st.button(button_text):
        st.session_state.show_recent_notices = not st.session_state.show_recent_notices

    if st.session_state.show_recent_notices:
        st.markdown('<div class="recent-notices" style="max-height: 400px; overflow-y: auto;">', unsafe_allow_html=True)

        recent_notices = get_recent_notices()
        if recent_notices:
            for notice in recent_notices:
                title, link, date = notice
                if isinstance(date, str):
                    date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
                formatted_date = date.strftime("%Y년 %m월 %d일") if language == '한국어' else date.strftime("%B %d, %Y")

                # 공지사항 카드 표시
                st.markdown(
                    f"""
                    <div class = "recent_notice" style='
                        border: 1px solid #ddd; 
                        border-radius: 8px; 
                        padding: 10px; 
                        margin-bottom: 12px; 
                        width: 100%;
                    '>
                        <h5 style='margin: 0; font-size: 1em; text-align: center;'>{title}</h5>
                        <p style='margin: 8px 0; font-size: 0.8em; text-align: center;'>{formatted_date}</p>
                        <a href='{link}' target='_blank' style='
                            text-decoration: none; 
                            color: white; 
                            background-color: #007BFF; 
                            padding: 6px 10px; 
                            border-radius: 4px; 
                            font-size: 0.8em; 
                            display: block; 
                            text-align: center;
                        '>{'공지 보기' if language == '한국어' else 'View Notice'}</a>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            no_notice_message = "최근 공지사항이 없습니다." if language == '한국어' else "No recent notices available."
            st.info(no_notice_message)
        st.markdown('</div>', unsafe_allow_html=True)

load_dotenv()


if 'message_list' not in st.session_state:
    st.session_state.message_list = []

# 자주 찾는 질문 버튼 스타일링
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&family=Montserrat:wght@400;700&display=swap');
    /* 기본 설정 */
    body {
        font-family: 'Roboto', sans-serif;
    }
    
    .st-emotion-cache-zkwxxx { /*간격 축소 */
        gap : 0.3rem;
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


with st.container():
    faq_title = "📌 자주 질문하는 정보" if language == '한국어' else "📌 Frequently Asked Questions"
    st.markdown('<div class="faq-section">', unsafe_allow_html=True)
    st.markdown(f'<div class="faq-title">{faq_title}</div>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)

    # 자주 질문하는 정보 버튼 클릭 시 정보들
faq_content = {
    '한국어': {
        "🗺️ 캠퍼스맵": """
            ### 캠퍼스맵 정보
            아래 이미지를 통해 한성대학교의 주요 건물과 시설 위치를 확인하세요.&nbsp;&nbsp;

            [한성대학교 캠퍼스맵](https://www.hansung.ac.kr/hansung/1773/subview.do#none)
            
            """,
        "🍴 학식": """
        ### 한성대학교 학식 정보
        한성대학교 학생 식당의 대표적인 메뉴와 운영 시간은 아래와 같습니다:

        - **운영 시간**: 학기중 11:00 ~ 19:00 (break time: 15:30 ~ 16:30), 방학중 11:00 ~ 17:00 (break time: 없음)

        [학식 정보](https://www.hansung.ac.kr/hansung/1920/subview.do)를 통해 확인할 수 있습니다.
        """,
"💰 등록금": """
### 2024학년도 2학기 등록금 정보

#### 등록기간 및 납부 대상자
- **납부 대상자**: 학부 재학생, 복학생
- **등록기간**:  
  - 일반 등록: **2024년 8월 23일(금) ~ 8월 30일(금)**  
  - 9학기 이상 학기초과자 등록: **2024년 9월 19일(목) ~ 9월 25일(수)**  
- **고지서 출력 가능일**: **2024년 8월 16일(금)**

#### 납부 방법
- **납부 은행**: 기업은행
- **납부 방법**: 고지서에 표기된 가상계좌로 인터넷뱅킹, ATM, 은행 창구에서 납부  
- **기타납입금**: 선택항목으로 가상계좌로 추가 납부 가능  

---

#### 6. 2024-2 학부 수업료 금액 (정규학기 8학기 이하)
| 단대/학과                   | 내국인 등록금      | 외국인 등록금      |
|---------------------------|-------------------|-------------------|
| 인문/사회대               | 3,239,000원      | 3,571,000원      |
| 예술대                    | 4,363,000원      | 4,810,000원      |
| 공대                      | 4,265,000원      | 4,702,000원      |
| 창의융합대                |                   |                   |
| - 상상력인재학부          | 3,530,000원      | 3,892,000원      |
| - 문학문화콘텐츠학과      | 3,239,000원      | 3,571,000원      |
| - AI응용학과              | 4,265,000원      | 4,702,000원      |
| 미래플러스대              |                   |                   |
| - 융합행정학과 등         | 3,239,000원      | -                 |
| - 뷰티디자인학과 등       | 3,589,000원      | -                 |
| 계약학과                  |                   |                   |
| - 뷰티매니지먼트학과      | 2,800,000원      | -                 |
| - 스마트제조혁신학과      | 2,450,000원      | -                 |

---

#### 7. 학기초과자 (9학기 이상 등록자)
| 단대/학과                   | 1~3학점 (1/6)     | 4~6학점 (1/3)     | 7~9학점 (1/2)     | 10학점 이상 (전액) |
|---------------------------|-------------------|-------------------|-------------------|-------------------|
| 인문/사회대               | 540,000원        | 1,080,000원      | 1,620,000원      | 3,239,000원      |
| 예술대                    | 727,000원        | 1,454,000원      | 2,182,000원      | 4,363,000원      |
| 공대                      | 711,000원        | 1,422,000원      | 2,133,000원      | 4,265,000원      |
| 외국인 (인문/사회대)      | 595,000원        | 1,190,000원      | 1,786,000원      | 3,571,000원      |
| 외국인 (예술대)           | 802,000원        | 1,603,000원      | 2,405,000원      | 4,810,000원      |
| 외국인 (공대)             | 784,000원        | 1,567,000원      | 2,351,000원      | 4,702,000원      |

---

#### 8. 문의
| 업무구분                     | 부서               | 전화번호          |
|---------------------------|-------------------|-------------------|
| 등록금 납부                | 재무회계팀        | 02-760-4233, 5623 |
| 교내/교외 장학금           | 학생장학팀        | 02-760-5602      |
| 등록금 환불, 휴학/복학 신청 | 학사지원팀        | 02-760-4219      |

자세한 등록금 금액 및 납부 안내는 [여기](https://www.hansung.ac.kr/hansung/8385/subview.do?enc=Zm5jdDF8QEB8JTJGYmJzJTJGaGFuc3VuZyUyRjE0MyUyRjI2MjY5OCUyRmFydGNsVmlldy5kbyUzRnBhZ2UlM0QxJTI2c3JjaENvbHVtbiUzRHNqJTI2c3JjaFdyZCUzRCVFQiU5MyVCMSVFQiVBMSU5RCVFQSVCOCU4OCUyNmJic0NsU2VxJTNEJTI2YmJzT3BlbldyZFNlcSUzRCUyNnJnc0JnbmRlU3RyJTNEJTI2cmdzRW5kZGVTdHIlM0QlMjZpc1ZpZXdNaW5lJTNEZmFsc2UlMjZwYXNzd29yZCUzRCUyNg%3D%3D)를 참조하세요.
""",
           "📝 시설 예약": """
            #### 세미나

            - **구분**: 상상베이스
            - **장소명**: 세미나실
            - **위치**: 상상관 B2층
            - **수용인원**: 6~16
            - **예약 페이지** : (https://www.hansung.ac.kr/onestop/8952/subview.do)

            #### 소그룹 활동

            - **위치**: 
                - [상상베이스](https://www.hansung.ac.kr/onestop/8952/subview.do) (상상관 B2층, IB 101~104)
                    - 접이식 가벽
                    - 수용 인원 : 4~8
                - [학술정보관](https://www.hansung.ac.kr/hsel/9611/subview.do) (학술정보관 3~6층)
                    - TV
                    - 수용 인원 : 3~11
                - [상상파크플러스](https://www.hansung.ac.kr/cncschool/7312/subview.do) (공학관 B1층)
                    - TV, 빔프로젝터
                    - 수용 인원 : 8

            #### 개별 학습

            - **위치**: 
                - 상상베이스 자유이용공간 (상상관 B2층)
                    - 개인 조명
                    - 수용 인원 : 50
                    - 자유 이용
                - [일반열람실 -집중열람실](https://hsel.hansung.ac.kr/home_login_write.mir) (일반열람실 4층)
                    - 노트북 이용 불가
                    - 수용 인원 : 162
                - [일반열람실 -우촌관열람실](https://hsel.hansung.ac.kr/home_login_write.mir) (우촌관 101호)
                    - 24시간 운영
                    - 수용 인원 : 55
                - 상상파크 상상라운지/오픈스튜디오 (연구관 1층)
                    - 오뜨 카페
                    - 수용 인원 : 150
                    - 자유 이용
                - 상상파크 C&C 멀티스튜디오 (연구관 1층)
                    - 공구류 이용
                    - 수용 인원 : 36
                    - 일정 없을시 자유 이용
                - 상상파크플러스 오픈공간 (공학관 B1층)
                    - 제본기
                    - 수용 인원 : 80
                    - 자유 이용
                    

            #### 기자재 이용

            - **위치**: 
                - 상상베이스 프린트존 (상상관 B2층)
                    - 출력, 문서 작업
                    - 자유 이용
                - [대학일자리플러스센터 AI 면접실](https://career.hansung.ac.kr/ko/commu/space/reservation) (상상관 B1층)
                    - 화상면접 지원
                    - 수용 인원 : 1
                - [상상파크 크레이티브 스튜디오](https://hansung.ac.kr/cncschool/7309/subview.do) (연구관 B1층)
                    - 3D 프린팅
                    - 수용 인원 : 30
                - [상상파크 디지털 머신룸](https://hansung.ac.kr/cncschool/7309/subview.do) (연구관 B1층)
                    - 레이저 커팅기
                    - 수용 인원 : 4
                - [상상파크 핸드크래프트룸](https://hansung.ac.kr/cncschool/7309/subview.do) (연구관 B1층)
                    - 스프레이부스 벨트 샌더
                    - 수용 인원 : 3

            #### 강의 제작 및 행사

            - **구분**: 영상 스튜디오
            - **장소명**: 디지털 스튜디오
            - **위치**: 미래관 1층
            - **수용인원**: 교직원
            - **특징**: 가상스튜디오시스템(크로마키), 프롬프터, 전자칠판 등
            - **예약 페이지** : (https://www.hansung.ac.kr/eist/6851/subview.do)

            #### 실습 강의 제작

            - **구분**: 영상 스튜디오
            - **장소명**: 실기 수업 콘텐츠 제작실
            - **위치**: 미래관 1층
            - **수용인원**: 교직원
            - **특징**: 다각도 카메라 (3대), 태블릿 등
            - **예약 페이지** : (https://www.hansung.ac.kr/eist/6852/subview.do)

            #### 화상 면접, 발표 영상 제작

            - **구분**: 영상 스튜디오
            - **장소명**: 미디어 콘텐츠 제작실
            - **위치**: 미래관 B105호
            - **수용인원**: 교직원
            - **특징**: 모니터링TV, 태블릿, 웹캠 등
            - **예약 페이지** : (https://www.hansung.ac.kr/eist/6853/subview.do)

            
            """
        },
    'English': {
        "🗺️ Campus Map": """
            ### Campus Map Information
            Below is the Hansung University campus map, showing the locations of major buildings and facilities.
            [Hansung University Campus Map](https://www.hansung.ac.kr/hansung/1773/subview.do#none)
            """,
        "🍴 Cafeteria": """ 
        ### Hansung University Cafeteria Information
        The operating hours of the Hansung University student cafeteria are as follows:

        - **Operating Hours**: During the semester: 11:00 AM ~ 7:00 PM (Break time: 3:30 PM ~ 4:30 PM),  
          During vacation: 11:00 AM ~ 5:00 PM

        For more detailed cafeteria information, visit [here](https://www.hansung.ac.kr/hansung/1920/subview.do).
        """,
"💰 Tuition": """
### 2024 Fall Semester Tuition
#### Payment Period and Eligibility
- **Eligible Students**: Undergraduate enrolled students and returning students.
- **Payment Period**:  
  - General Registration: **August 23, 2024 (Friday) – August 30, 2024 (Friday)**  
  - Registration for 9+ semesters: **September 19, 2024 (Thursday) – September 25, 2024 (Wednesday)**  
- **Invoice Availability**: **August 16, 2024 (Friday)**

#### Payment Methods
- **Bank**: IBK Industrial Bank of Korea (기업은행)
- **Method**: Transfer to the designated virtual account indicated on the invoice via internet banking, ATM, or bank teller.  
- **Additional Fees**: Optional fees can be paid via the virtual account.

---

#### 6. 2024-2 Undergraduate Tuition Fees (Regular Semester, Up to 8 Semesters)
| College/Department            | Domestic Tuition  | International Tuition  |
|-------------------------------|-------------------|------------------------|
| Humanities/Social Sciences    | 3,239,000 KRW     | 3,571,000 KRW          |
| Arts                          | 4,363,000 KRW     | 4,810,000 KRW          |
| Engineering                   | 4,265,000 KRW     | 4,702,000 KRW          |
| Creative Convergence          |                   |                        |
| - Creative Talents Division   | 3,530,000 KRW     | 3,892,000 KRW          |
| - Literature/Content Studies  | 3,239,000 KRW     | 3,571,000 KRW          |
| - AI Applications             | 4,265,000 KRW     | 4,702,000 KRW          |
| Future Plus Division          |                   |                        |
| - Convergence Admin./Business | 3,239,000 KRW     | -                      |
| - Beauty/I.T. Design          | 3,589,000 KRW     | -                      |
| Contract-Based Majors         |                   |                        |
| - Beauty Management           | 2,800,000 KRW     | -                      |
| - Smart Manufacturing         | 2,450,000 KRW     | -                      |

---

#### 7. Over-Semester Students (9+ Semesters)
| College/Department            | 1–3 Credits (1/6) | 4–6 Credits (1/3) | 7–9 Credits (1/2) | 10+ Credits (Full) |
|-------------------------------|-------------------|-------------------|-------------------|-------------------|
| Humanities/Social Sciences    | 540,000 KRW       | 1,080,000 KRW     | 1,620,000 KRW     | 3,239,000 KRW     |
| Arts                          | 727,000 KRW       | 1,454,000 KRW     | 2,182,000 KRW     | 4,363,000 KRW     |
| Engineering                   | 711,000 KRW       | 1,422,000 KRW     | 2,133,000 KRW     | 4,265,000 KRW     |
| International (Humanities)    | 595,000 KRW       | 1,190,000 KRW     | 1,786,000 KRW     | 3,571,000 KRW     |
| International (Arts)          | 802,000 KRW       | 1,603,000 KRW     | 2,405,000 KRW     | 4,810,000 KRW     |
| International (Engineering)   | 784,000 KRW       | 1,567,000 KRW     | 2,351,000 KRW     | 4,702,000 KRW     |

---

#### 8. Inquiries
| Area                            | Department         | Contact            |
|---------------------------------|--------------------|--------------------|
| Tuition Payment                 | Financial Team     | 02-760-4233, 5623 |
| External/Internal Scholarships  | Student Scholarship| 02-760-5602       |
| Tuition Receipts / Refunds      | Academic Support   | 02-760-4219       |

For detailed tuition fees and payment guidance, please refer to [here](https://www.hansung.ac.kr/hansung/8385/subview.do?enc=Zm5jdDF8QEB8JTJGYmJzJTJGaGFuc3VuZyUyRjE0MyUyRjI2MjY5OCUyRmFydGNsVmlldy5kbyUzRnBhZ2UlM0QxJTI2c3JjaENvbHVtbiUzRHNqJTI2c3JjaFdyZCUzRCVFQiU5MyVCMSVFQiVBMSU5RCVFQSVCOCU4OCUyNmJic0NsU2VxJTNEJTI2YmJzT3BlbldyZFNlcSUzRCUyNnJnc0JnbmRlU3RyJTNEJTI2cmdzRW5kZGVTdHIlM0QlMjZpc1ZpZXdNaW5lJTNEZmFsc2UlMjZwYXNzd29yZCUzRCUyNg%3D%3D).
""",
            "📝 Facility": """
            #### Seminar

            - **Category**: Imagination Base
            - **Location Name**: Seminar Room
            - **Location**: Imagination Hall, B2 Floor
            - **Capacity**: 6–16
            - **Reservation Page**: (https://www.hansung.ac.kr/onestop/8952/subview.do)

            #### Small Group Activities

            - **Location**: 
                - [Imagination Base](https://www.hansung.ac.kr/onestop/8952/subview.do) (Imagination Hall, B2 Floor, IB 101~104)
                    - Folding partitions
                    - Capacity: 4–8
                - [Library](https://www.hansung.ac.kr/hsel/9611/subview.do) (Library, Floors 3–6)
                    - TV available
                    - Capacity: 3–11
                - [Imagination Park Plus](https://www.hansung.ac.kr/cncschool/7312/subview.do) (Engineering Hall, B1 Floor)
                    - TV, projector available
                    - Capacity: 8

            #### Individual Study

            - **Location**: 
                - Free-use space at Imagination Base (Imagination Hall, B2 Floor)
                    - Individual lighting available
                    - Capacity: 50
                    - Free access
                - [General Reading Room – Concentration Room](https://hsel.hansung.ac.kr/home_login_write.mir) (General Reading Room, 4th Floor)
                    - Laptops not allowed
                    - Capacity: 162
                - [General Reading Room – Uchong Hall](https://hsel.hansung.ac.kr/home_login_write.mir) (Uchong Hall, Room 101)
                    - 24/7 Operation
                    - Capacity: 55
                - Imagination Park Lounge/Open Studio (Research Hall, 1st Floor)
                    - Ott Café
                    - Capacity: 150
                    - Free access
                - Imagination Park C&C Multi-Studio (Research Hall, 1st Floor)
                    - Tool usage
                    - Capacity: 36
                    - Free access if no schedule
                - Imagination Park Plus Open Space (Engineering Hall, B1 Floor)
                    - Binding machine
                    - Capacity: 80
                    - Free access

            #### Equipment Usage

            - **Location**: 
                - Imagination Base Print Zone (Imagination Hall, B2 Floor)
                    - Printing, document work
                    - Free access
                - [University Job Plus Center AI Interview Room](https://career.hansung.ac.kr/ko/commu/space/reservation) (Imagination Hall, B1 Floor)
                    - Support for video interviews
                    - Capacity: 1
                - [Imagination Park Creative Studio](https://hansung.ac.kr/cncschool/7309/subview.do) (Research Hall, B1 Floor)
                    - 3D Printing
                    - Capacity: 30
                - [Imagination Park Digital Machine Room](https://hansung.ac.kr/cncschool/7309/subview.do) (Research Hall, B1 Floor)
                    - Laser cutter
                    - Capacity: 4
                - [Imagination Park Handcraft Room](https://hansung.ac.kr/cncschool/7309/subview.do) (Research Hall, B1 Floor)
                    - Spray booth, belt sander
                    - Capacity: 3

            #### Lecture Production and Events

            - **Category**: Video Studio
            - **Location Name**: Digital Studio
            - **Location**: Future Hall, 1st Floor
            - **Capacity**: Faculty
            - **Features**: Virtual studio system (chroma key), teleprompter, electronic whiteboard, etc.
            - **Reservation Page**: (https://www.hansung.ac.kr/eist/6851/subview.do)

            #### Practical Lecture Production

            - **Category**: Video Studio
            - **Location Name**: Practical Class Content Production Room
            - **Location**: Future Hall, 1st Floor
            - **Capacity**: Faculty
            - **Features**: Multi-angle cameras (3 units), tablet, etc.
            - **Reservation Page**: (https://www.hansung.ac.kr/eist/6852/subview.do)

            #### Video Interviews and Presentation Production

            - **Category**: Video Studio
            - **Location Name**: Media Content Production Room
            - **Location**: Future Hall, B105
            - **Capacity**: Faculty
            - **Features**: Monitoring TV, tablet, webcam, etc.
            - **Reservation Page**: (https://www.hansung.ac.kr/eist/6853/subview.do)
"""
        }
    }

if "faq_buttons" not in st.session_state:
    if language == '한국어':
        st.session_state.faq_buttons = {key: False for key in faq_content['한국어'].keys()}
    else:
        st.session_state.faq_buttons = {key: False for key in faq_content['English'].keys()}

for i, (button_text, content) in enumerate(faq_content[language].items()):  
    with [col1, col2, col3, col4][i]:
        button_clicked = st.session_state.faq_buttons.get(button_text, False)
        if st.button(button_text, key=f"button_{button_text}"):
            st.session_state.faq_buttons[button_text] = not button_clicked
            for key in st.session_state.faq_buttons:
                if key != button_text:
                    st.session_state.faq_buttons[key] = False

for button_text, is_clicked in st.session_state.faq_buttons.items():
    if is_clicked:
        # 선택된 버튼에 대한 키값을 설정
        faq_key = button_text if language == '한국어' else {
            "🍴 학식": "🍴 Cafeteria",
            "🗺️ 캠퍼스맵": "🗺️ Campus Map",
            "💰 등록금": "💰 Tuition",
            "📝 시험일정": "📝 Exam Schedule"
        }.get(button_text, button_text)

        if faq_key not in faq_content[language]:
            st.error("해당 항목에 대한 정보를 찾을 수 없습니다.")
            continue

        # FAQ 콘텐츠 로드
        content = faq_content[language][faq_key]
        
        
        # FAQ 콘텐츠 표시
        st.markdown(
            f"""
            <div class ="faq-content">
                {content}
            """,
            unsafe_allow_html=True,
        )

        # 캠퍼스 맵
        if faq_key in ["🗺️ 캠퍼스맵", "🗺️ Campus Map"]:
            st.image(
                "./image/map.png",
                caption="한성대학교 캠퍼스맵" if language == '한국어' else "Hansung University Campus Map",
                use_column_width=True
            )

        # 학식 사진 갤러리
        if faq_key in ["🍴 학식", "🍴 Cafeteria"]:
            st.markdown("#### 학식 사진" if language == '한국어' else "Cafeteria Photo")

         # 각 이미지를 한 줄에 하나씩 세로로 표시
            st.image(
            "./image/10.jpg",
             use_column_width=True
          )
            st.image(
            "./image/11.jpg",
            use_column_width=True
        )
            st.image(
            "./image/12.jpg",
            use_column_width=True
        )
            st.image(
            "./image/13.jpg",
            use_column_width=True
        )
# 스타일 유지
st.markdown("""
    <style>
    .faq-content {
        padding: 20px;
        margin-top: 20px;
        border-radius: 12px;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.3);
        font-size: 1.1em;
        line-height: 1.6;
    }
    .stButton>button[aria-pressed="true"] {
        background-color: #555555 !important;
        color: #ffffff !important;
        font-weight: bold !important;
        border: 2px solid #888888 !important;
    }
    </style>
""", unsafe_allow_html=True)

recommended_notices = st.session_state.get('recommended_notices', [])  # 기본값은 빈 리스트

# 세션에서 학과 정보가 있으면 추천 공지사항을 가져와서 출력
if "department" in st.session_state:
    
    st.markdown("""
    <style>
        .notice-item {
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.2);
            padding: 15px;
            margin: 10px 0;
            width: 100%;
            transition: transform 0.2s;
        }
        .notice-item:hover {
            transform: translateY(-5px);
        }
        .notice-title {
            text-decoration: none;
            font-size: 1em;
        }
        .notice-date {
            font-size: 0.9em;
        }
    </style>
    """, unsafe_allow_html=True)



# 추천 공지사항이 있으면 출력
if recommended_notices:
    st.subheader("📌 Recommended Notices" if language != "한국어" else "📌 추천 공지사항")

    department = st.session_state.get(
        'department', 
        'No Department Info' if language != "한국어" else '학과 정보 없음'
    )
    
    # 학과 정보 출력 (가운데 정렬 및 배경 박스 추가)
    st.markdown(f"""
    <div style='
        background-color: #f7f7f7;
        border-radius: 8px;
        padding: 10px;
        margin-bottom: 20px;
        width: fit-content;
        margin-left: auto;
        margin-right: auto;
        font-size: 0.9em;
        text-align: center;
        color: #333;
    '>
        <strong>{"Department: " + department if language != "한국어" else "학과 : " + department}</strong>
    </div>
    """, unsafe_allow_html=True)
    
    for notice in recommended_notices:
        # 공지사항 제목, 링크, 날짜를 가져옵니다
        title = notice['title']
        link = notice['link']
        date = notice['date']
        
        # 날짜 형식 처리
        if isinstance(date, str):
            date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        formatted_date = date.strftime("%B %d, %Y") if language != "한국어" else date.strftime("%Y년 %m월 %d일")
        
        # 각 공지사항을 박스로 둘러싸기
        st.markdown(f"""
        <div class="notice-item" style='
            border: 1px solid #ddd; 
            border-radius: 8px; 
            padding: 10px; 
            margin-bottom: 21px; 
            width: 100%;
        '>
            <h5 style='margin: 0; font-size: 1em; text-align: center;'>{title}</h5>
            <p style='margin: 8px 0; font-size: 0.8em; text-align: center;'>{formatted_date}</p>
            <a href='{link}' target='_blank' style='
                text-decoration: none; 
                color: white; 
                background-color: #007BFF; 
                padding: 6px 10px; 
                border-radius: 4px; 
                font-size: 0.8em; 
                display: block; 
                text-align: center;
                margin-top: 10px;
            '>{'View Notice' if language != "한국어" else '공지 보기'}</a>
        </div>
        """, unsafe_allow_html=True)

else:
    st.write("No recommended notices available." if language != "한국어" else "추천 공지사항이 없습니다.")

if 'department' not in st.session_state:
    st.write("Department information is not in the session. Please log in and try again." if language != "한국어" else "학과 정보가 세션에 없습니다. 로그인 후 다시 시도해주세요.")



if 'message_list' not in st.session_state:
    st.session_state.message_list = []

for message in st.session_state.message_list:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 사용자 입력 처리
if user_question := st.chat_input(placeholder="한성대에 관련된 궁금한 내용들을 말씀해주세요!"):
    # 사용자 입력을 채팅에 표시
    with st.chat_message("user"):
        st.write(user_question)
    st.session_state.message_list.append({"role": "user", "content": user_question})

    # AI 응답 생성
    spinner_message = "답변을 생성하는 중입니다..." if language == "한국어" else "Generating a response..."
    with st.spinner(spinner_message):  # 언어에 따라 스피너 메시지 변경
        ai_response = get_ai_response(user_question, language=language)  # 언어 인자 전달
        with st.chat_message("ai"):
            ai_message = st.write_stream(ai_response)
        st.session_state.message_list.append({"role": "ai", "content": ai_message})
