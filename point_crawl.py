import requests
from bs4 import BeautifulSoup as bs
import mysql.connector
from datetime import datetime

# MySQL 연결 설정
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="12345678",
    database="crawled"
)
cursor = db.cursor()

# 테이블이 없으면 생성
create_table_query = """
CREATE TABLE IF NOT EXISTS point (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255),
    link TEXT,
    date DATETIME
)
"""
cursor.execute(create_table_query)

# RSS 피드 URL
rss_url = 'https://rss.app/feeds/4eUf9tubErGoFqS2.xml'

# RSS 피드 요청
response = requests.get(rss_url)

if response.status_code == 200:
    soup = bs(response.text, 'xml')
    articles = soup.find_all('item')

    for article in articles:
        title = article.find('title').get_text(strip=True) if article.find('title') else "No Title"
        link = article.find('link').get_text(strip=True) if article.find('link') else "No Link"
        pub_date = article.find('pubDate').get_text(strip=True) if article.find('pubDate') else "No Date"

        # 날짜 형식 변환
        try:
            # 'Mon, 25 Nov 2024 06:00:00 GMT' 형식을 MySQL DATETIME 형식으로 변환
            date_obj = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %Z')
            mysql_date_str = date_obj.strftime('%Y-%m-%d %H:%M:%S')
        except ValueError as e:
            print(f"날짜 변환 오류: {pub_date} - {e}")
            mysql_date_str = None  # 변환 실패 시 None으로 설정

        # MySQL 테이블에 저장
        if mysql_date_str:  # 날짜가 변환된 경우에만 저장
            sql = "INSERT INTO point (title, link, date) VALUES (%s, %s, %s)"
            val = (title, link, mysql_date_str)
            cursor.execute(sql, val)
            db.commit()

            # 저장된 데이터 출력
            print(f"제목: {title}")
            print(f"링크: {link}")
            print(f"게시 날짜: {mysql_date_str}")
            print("-" * 40)  # 구분선 출력
else:
    print("RSS 피드를 가져오는 데 실패했습니다:", response.status_code)

# MySQL 연결 종료
cursor.close()
db.close()

print("모든 공지사항이 성공적으로 저장되었습니다.")
