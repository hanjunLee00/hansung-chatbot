from dotenv import load_dotenv
import streamlit as st
from llm import get_ai_response
from PIL import Image
from datetime import datetime
import requests
from bs4 import BeautifulSoup as bs


# 최신 3개의 공지사항을 크롤링하는 메소드
def get_recent_notices(limit=3):
    base_url = 'https://www.hansung.ac.kr/bbs/hansung/143/rssList.do?page=1'  # 첫 페이지만 사용
    notices = []

    page = requests.get(base_url)
    soup = bs(page.text, 'xml')
    articles = soup.find_all('item')
    base_domain = "https://www.hansung.ac.kr"

    for article in articles[:limit]:  # 최신 공지사항 3개만 처리
        title = article.find('title').get_text(strip=True) if article.find('title') else "No Title"
        link = article.find('link').get_text() if article.find('link') else "No Link"
        pub_date = article.find('pubDate').get_text(strip=True) if article.find('pubDate') else "No Date"

        if link.startswith("/"):
            link = f"{base_domain}{link}"

        # 공지사항 정보를 notices 리스트에 추가
        notices.append((title, link, pub_date))

    return notices

icon_image = Image.open("./hansungbu.png")

# 사용자 지정 아이콘으로 페이지 구성 설정
st.set_page_config(page_title="한성대학교 챗봇", page_icon=icon_image)

# CSS 파일 불러오기
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# 탭기능 - 언어선택
st.sidebar.title("언어 선택 / Language Selection")
language = st.sidebar.radio("Choose Language", ('한국어', 'English'), key= "language_selector")

if 'theme' not in st.session_state:
    st.session_state.theme = "라이트 모드"  # 기본값을 라이트 모드로 설정

# Sidebar 테마 설정
st.sidebar.subheader("테마 설정" if language == '한국어' else "Theme Settings")
theme = st.sidebar.radio(
    "테마 선택" if language == '한국어' else "Select Theme", 
    ["다크 모드" if language == '한국어' else "Dark Mode", 
     "라이트 모드" if language == '한국어' else "Light Mode"], 
    key="theme_selector"
)

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
            .notice-card {
                border: 1px solid #444; 
                border-radius: 8px; 
                padding: 10px; 
                margin-bottom: 12px; 
                width: 100%; 
                background-color: #333;
                color: #ddd;
            }
                .notice-card h5 {
                margin: 0; 
                color: #66ccff; 
                font-size: 1em; 
                text-align: center;
            }
            .notice-card h5 a {
                text-decoration: none; 
                color: #66ccff;
            }
            .notice-card h5 a:hover {
                color: #99ddff;
            }
            .notice-card p {
                margin: 8px 0; 
                font-size: 0.8em; 
                color: #bbb; 
                text-align: center;
            }
            .caption {
                color : white;
            }
            .stApp { 
                background-color: #0f0f0f;
            }
             h1, h3 {
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
            .st-emotion-cache-uuorpk {
                color : #b1b1b1;
            }
            .faq-section {
                background-color: #1c1c1c;
            }
            .faq-title {
                font-size: 25px;
                color: #f5f5f5;
                padding: 12px;
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
            .st-d1 { /* 텍스트창 */
                background-color: #444444;
            }
            .st-d1::placeholder {
                color : #9c9c9c;
            }
            .notice-item {
                background-color : #333;
            }
            .recent_notice {
                background-color : #333;
                color : white;
            }
            .st-emotion-cache-uuorpk{
                color : #b1b1b1;
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
            .notice-card {
                border: 1px solid #ddd; 
                border-radius: 8px; 
                padding: 10px; 
                margin-bottom: 12px; 
                width: 100%; 
                background-color: #f9f9f9;
                color: #333;
            }
            .notice-card h5 {
                margin: 0; 
                color: #007BFF; 
                font-size: 1em; 
                text-align: center;
            }
            .notice-card h5 a {
                text-decoration: none; 
                color: #007BFF;
            }
            .notice-card h5 a:hover {
                color: #0056b3;
            }
            .notice-card p {
                margin: 8px 0; 
                font-size: 0.8em; 
                color: #555; 
                text-align: center;
            }
            .caption {
                color : black;
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
                font-size: 25px;
                color: #333;
                padding: 12px;
            }
            .st-emotion-cache-1c7y2kd { /* 질문자 메시지 스타일 */
                background-color : #f9f9f9;
            }
            .notice-item {
                background-color : #f9f9f9;
            }
        </style>
    """, unsafe_allow_html=True)

# 탭기능 - 사용자 안내서
st.sidebar.subheader("사용자 안내서" if language == '한국어' else "User Guide")
if "show_guide" not in st.session_state:
    st.session_state.show_guide = False

if st.sidebar.button("자세히 보기" if language == '한국어' else "View Details"):
    st.session_state.show_guide = not st.session_state.show_guide  

if st.session_state.show_guide:
    if language == '한국어':
        st.sidebar.markdown("""
        - **질문을 간결하게 작성하세요**: 명확하고 짧은 질문이 더 정확한 답변을 제공합니다.
        - **한성대 관련 정보만 제공**: 학업, 캠퍼스, 장학금 등 한성대 관련 정보에 집중되어 있습니다.
        """)
    else:
        st.sidebar.markdown("""
        - **Ask concise questions**: Clear and short questions lead to more accurate answers.
        - **
                            Information related to Hansung University only**: Focuses on academics, campus, scholarships, etc., relevant to Hansung University.
        """)

# 탭기능 - 에브리타임 바로가기
st.sidebar.subheader("한성대학교 에브리타임 바로가기" if language == '한국어' else "Hansung University Everytime Shortcut")
if "show_everytime" not in st.session_state:
    st.session_state.show_everytime = False

if st.sidebar.button("한성대학교 에브리타임" if language == '한국어' else "Hansung University Everytime", key="everytime_button"):
    st.session_state.show_everytime = not st.session_state.show_everytime  

if st.session_state.show_everytime:
    st.sidebar.markdown(
        "[에브리타임 바로가기](https://hansung.everytime.kr/)" if language == '한국어' else "[Everytime Shortcut](https://hansung.everytime.kr/)",
        unsafe_allow_html=True
    )

title_icon = Image.open("./hansungbu.png")

# 언어에 따라 타이틀과 캡션을 설정
if language == '한국어':
    title_text = "한성대학교 챗봇"
    caption = "한성대에 관련된 모든 것을 답해드립니다!"
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
        st.markdown(f'<p class = "caption">{caption}</p>', unsafe_allow_html=True)

with col2:
    if "show_recent_notices" not in st.session_state:
        st.session_state.show_recent_notices = False

    button_text = "📢 최근 공지사항 보기" if language == '한국어' else "📢 View Recent Notices"
    
    if st.button(button_text):
        st.session_state.show_recent_notices = not st.session_state.show_recent_notices

    if st.session_state.show_recent_notices:
        st.markdown('<div class="recent-notices" style="max-height: 400px; overflow-y: auto;">', unsafe_allow_html=True)

        recent_notices = get_recent_notices()  # 최신 3개의 공지사항 가져오기
        if recent_notices:
            for notice in recent_notices:
                title, link, pub_date = notice
                
                # 날짜 포맷팅 (pub_date가 문자열인 경우)
                if isinstance(pub_date, str):
                    formatted_date = pub_date  # pub_date가 이미 문자열이므로 변환 필요 없음
                else:
                    formatted_date = pub_date.strftime("%Y년 %m월 %d일") if language == '한국어' else pub_date.strftime("%B %d, %Y")

                # 공지사항 카드 표시
                st.markdown(
                f"""
                <div class="notice-card">
                    <h5>
                        <a href='{link}' target='_blank'>{title}</a>
                    </h5>
                    <p>게시일: {formatted_date}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
                  
        else:
            no_notice_message = "최근 공지사항이 없습니다." if language == '한국어' else "No recent notices available."
            st.info(no_notice_message)

        st.markdown('</div>', unsafe_allow_html=True)


load_dotenv()

# 자주 찾는 질문 버튼 스타일링
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&family=Montserrat:wght@400;700&display=swap');
    body { font-family: 'Roboto', sans-serif; color: #f0f0f0; background-color: #2b2b2b; }
    .faq-section { background-color: #333333; padding: 15px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.5); margin-bottom: 20px; }
    # .faq-title { font-family: 'Montserrat', sans-serif; font-size: 1.3em; font-weight: 700; color: #ffffff; margin-bottom: 15px; text-align: center; }
    .stButton>button { font-family: 'Roboto', sans-serif; width: 100%; padding: 12px; border-radius: 8px; background-color: #444444; color: #e0e0e0; box-shadow: 0 2px 5px rgba(0, 0, 0, 0.4); border: 1px solid #555555; transition: background-color 0.3s, box-shadow 0.3s, transform 0.3s ease; }
    .stButton>button:hover { background-color: #555555; box-shadow: 0 4px 8px rgba(255, 255, 255, 0.2); transform: scale(1.05); }
    .chat-message-user { background-color: #3a3a3a; color: #ffffff; padding: 12px 18px; border-radius: 10px; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.3); }
    .chat-message-bot { background-color: #4b4b4b; color: #e0e0e0; padding: 12px 18px; border-radius: 10px; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.2); }
    </style>
""", unsafe_allow_html=True)


with st.container():
    st.markdown('<div class="faq-section">', unsafe_allow_html=True)
    st.markdown('<div class="faq-title">📌 자주 질문하는 정보</div>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)

    # 자주 질문하는 정보 버튼 클릭 시 정보들
    faq_content = {
        '한국어': {
            "🎓 장학금": """
            ### 2024학년도 2학기 교내 장학금 종류
            1. **다자녀 장학금**: 세 자녀 이상(다자녀) 가정 중 본교에 재학하는 자녀가 있는 경우.
            2. **가족 장학금**: 본교 가족이 2인 이상 동시에 재학 중인 경우.
            3. **장애학생 복지 장학금**: 본교 재학 중인 학생으로서 장애인복지법에 의거 장애인으로 등록된 자.
            4. **다문화가정 지원 장학금**: 다문화가정의 자녀로서 대한민국 국적자의 재학생.

            자세한 내용은 [여기](https://hansung.everytime.kr/scholarship)에서 확인하실 수 있습니다.
            """,
            "🗺️ 캠퍼스맵": """
            ### 캠퍼스맵 정보
            아래 이미지를 통해 한성대학교의 주요 건물과 시설 위치를 확인하세요.
            [한성대학교 캠퍼스맵](https://www.hansung.ac.kr/hansung/1773/subview.do#none)
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
            "📝 시험일정": """
            ### 2024학년도 2학기 시험일정
            시험일정 및 시간표는 학사 공지사항을 통해 확인하실 수 있습니다.
            자세한 내용은 [여기](https://hansung.everytime.kr/examschedule)를 참조하세요.
            """
        },
        'English': {
            "🎓 Scholarships": """
            ### 2024 Fall Semester Scholarships
            1. **Multichild Scholarship**: Families with three or more children enrolled at the university.
            2. **Family Scholarship**: Families with two or more members simultaneously enrolled.
            3. **Disability Welfare Scholarship**: Students officially registered as disabled under the Welfare Law.
            4. **Multicultural Family Support Scholarship**: Students from multicultural families with Korean nationality.

            For details, visit [here](https://hansung.everytime.kr/scholarship).
            """,
            "🗺️ Campus Map": """
            ### Campus Map Information
            Below is the Hansung University campus map, showing the locations of major buildings and facilities.
            [Hansung University Campus Map](https://www.hansung.ac.kr/hansung/1773/subview.do#none)
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
            "📝 Exam Schedule": """
            ### 2024 Fall Semester Exam Schedule
            Check the academic announcements for exam schedules and timetables.
            Find more details [here](https://hansung.everytime.kr/examschedule).
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
        faq_key = button_text if language == '한국어' else {
            "🎓 장학금": "🎓 Scholarships",
            "🗺️ 캠퍼스맵": "🗺️ Campus Map",
            "💰 등록금": "💰 Tuition",
            "📝 시험일정": "📝 Exam Schedule"
        }.get(button_text, button_text)

        if faq_key not in faq_content[language]:
            st.error("해당 항목에 대한 정보를 찾을 수 없습니다.")
            continue

        st.markdown(
            f"""
            <div class="faq-content">
                {faq_content[language][faq_key]}
            </div>
            """,
            unsafe_allow_html=True, 
        )

        if faq_key in ["🗺️ 캠퍼스맵", "🗺️ Campus Map"]:
            st.image("./map.png", caption="한성대학교 캠퍼스맵", use_column_width=True)

    st.markdown('</div>', unsafe_allow_html=True)


st.markdown("""
    <style>
    .faq-content {
        background-color: #222222;
        padding: 20px;
        margin-top: 20px;
        border-radius: 12px;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.3);
        color: #ffffff;
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

if 'message_list' not in st.session_state:
    st.session_state.message_list = []

# Display past messages
for message in st.session_state.message_list:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.write(message["content"])
    elif message["role"] == "ai":
        with st.chat_message("ai"):
            st.write(message["content"])

# Chat input for custom questions
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
