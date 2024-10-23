import requests
from bs4 import BeautifulSoup as bs
import mysql.connector
import time

# Step 1: MySQL에 연결
db = mysql.connector.connect(
    host="localhost",        # MySQL 호스트 (예: 'localhost')
    user="root",    # MySQL 사용자 이름
    password="12345678",  # MySQL 비밀번호
    database="crawled"    # 데이터베이스 이름
)

cursor = db.cursor()

# 테이블이 존재하지 않으면 생성하는 SQL
create_table_query = """
CREATE TABLE IF NOT EXISTS swfree (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255),
    content TEXT,
    pubDate DATETIME,
    savedDate DATETIME
)
"""
cursor.execute(create_table_query)

base_url = "https://www.hansung.ac.kr/bbs/hansung/143/rssList.do?row=1000"
# total_page = 170

# BeautifulSoup으로 HTML 파싱
def fetch_notice_titles_and_date(base_url):
    page = requests.get(base_url)
    soup = bs(page.text, 'html.parser')

    # <item> 태그 내에서 공지사항 제목 추출
    articles = soup.find_all('item')
    crawled_data = []

    for article in articles:
        title_tag = article.find('title')
        pubDate_tag = article.find('pubDate')
        title = title_tag.get_text(strip=True) if title_tag else "No Title"
        pubDate = pubDate_tag.get_text(strip=True) if pubDate_tag else "No puubDate"
        crawled_data.append(title, pubDate)

    return crawled_data

def save_to_db_table():

    sql= "INSERT INTO swfree (title, pubDate) VALUES (%s, %s)"
    val = (fetch_notice_titles_and_date)
    cursor.execute(sql, val)
    db.commit()
    #공지사항 제목 추출

#sql 연결 종료
cursor.close()
db.close()



