import requests
from bs4 import BeautifulSoup as bs
import mysql.connector

# 공지사항 내용을 크롤링하는 함수
def content_croll(url):
    page = requests.get(url)
    # BeautifulSoup으로 HTML 파싱
    soup = bs(page.text, 'html.parser')
    # <div> 태그 내에서 공지사항 내용을 추출 (클래스가 'view-con'인 부분)
    view_con_div = soup.find('div', class_='view-con')
    
    # 내용 추출
    if view_con_div:
        content = view_con_div.get_text(strip=True)
    else:
        content = "No content found"
    
    return content

# Step 1: MySQL에 연결
db = mysql.connector.connect(
    host="localhost",        # MySQL 호스트
    user="root",             # MySQL 사용자 이름
    password="12345678", # MySQL 비밀번호
    database="crawled"        # 데이터베이스 이름
)

cursor = db.cursor()

# 테이블이 존재하지 않으면 생성하는 SQL (이미 테이블이 있으면 생략 가능)
create_table_query = """
CREATE TABLE IF NOT EXISTS swfree (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255),
    link TEXT,
    content TEXT,           -- 공지사항 내용을 저장할 필드 추가
    date DATETIME           -- 공지사항 날짜를 저장할 필드 추가
)
"""
cursor.execute(create_table_query)

# Step 2: RSS 피드에서 공지사항 제목, 링크, 내용, 날짜 가져오기
url = 'https://www.hansung.ac.kr/bbs/hansung/143/rssList.do?row=1000'
page = requests.get(url)

# BeautifulSoup으로 XML 파싱
soup = bs(page.text, 'xml')

# <item> 태그 내에서 공지사항 제목과 링크 추출
articles = soup.find_all('item')

# 기본 URL 설정 (상대 경로에 사용할 도메인)
base_url = "https://www.hansung.ac.kr/"

for article in articles:
    
    # 공지사항 제목 추출
    title_tag = article.find('title')
    title = title_tag.get_text(strip=True) if title_tag else "No Title"

    # 공지사항 링크 추출 (링크는 상대 경로로 주어짐)
    link_tag = article.find('link')
    link = link_tag.get_text() if link_tag else "No Link"

    # 공지사항 날짜 추출
    pub_date_tag = article.find('pubDate')
    pub_date = pub_date_tag.get_text(strip=True) if pub_date_tag else "No Date"

    # 상대 경로를 절대 경로로 변환
    if link.startswith("/"):
        link = base_url + link[1:]
    
    # 공지사항 내용 크롤링
    content = content_croll(link)

    # 제목, 링크, 내용 및 날짜 출력 (확인용)
    print(f"title: {title}")
    print(f"Link: {link}")
    print(f"Content: {content}")
    print(f"Date: {pub_date}")
    
    # Step 3: MySQL 테이블에 제목, 링크, 내용, 날짜 삽입
    sql = "INSERT INTO swfree (title, link, content, date) VALUES (%s, %s, %s, %s)"
    val = (title, link, content, pub_date)
    cursor.execute(sql, val)
    db.commit()  # 변경 사항 저장

# MySQL 연결 종료
cursor.close()
db.close()

print("모든 공지사항 제목, 링크, 내용, 날짜가 성공적으로 저장되었습니다.")
