import requests
from bs4 import BeautifulSoup as bs
import mysql.connector
from datetime import datetime

# 공지사항 내용을 크롤링하는 함수
def content_croll(url):
    page = requests.get(url)
    soup = bs(page.text, 'html.parser')
    view_con_div = soup.find('div', class_='view-con')

    content = ""
    image_url = None
    if view_con_div:
        content = view_con_div.get_text(strip=True)

        # 이미지 URL을 찾기
        image_tag = view_con_div.find('img')
        if image_tag and 'src' in image_tag.attrs:
            image_url = image_tag['src']
    
    else:
        content = "No content found"
    
    return content, image_url

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
CREATE TABLE IF NOT EXISTS swpre (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255),
    link TEXT,
    content TEXT,
    image TEXT,
    date DATETIME
)
"""
cursor.execute(create_table_query)

# 가장 최신 공지사항 날짜를 가져옴
cursor.execute("SELECT MAX(date) FROM swpre")
last_crawled_date = cursor.fetchone()[0]

if not last_crawled_date:
    last_crawled_date = datetime.min  # 데이터가 없으면 가장 과거 날짜로 설정

# 최신 공지사항 페이지 순회
base_url = 'https://www.hansung.ac.kr/bbs/hansung/143/rssList.do?page={}'

# 카운트
count = 0

# 가장 오래된 새 공지사항 날짜를 저장할 변수
oldest_new_date = None

for page_number in range(1, 10):
    url = base_url.format(page_number)
    page = requests.get(url)
    soup = bs(page.text, 'xml')
    articles = soup.find_all('item')
    base_domain = "https://www.hansung.ac.kr"

    for article in articles:
        title = article.find('title').get_text(strip=True) if article.find('title') else "No Title"
        link = article.find('link').get_text() if article.find('link') else "No Link"
        pub_date = article.find('pubDate').get_text(strip=True) if article.find('pubDate') else "No Date"

        # pubDate를 datetime 형식으로 변환
        try:
            pub_date = datetime.strptime(pub_date, '%Y-%m-%d %H:%M:%S.%f')  # 형식: 'YYYY-MM-DD HH:MM:SS.s'
        except ValueError:
            try:
                pub_date = datetime.strptime(pub_date, '%Y-%m-%d %H:%M:%S')  # 형식: 'YYYY-MM-DD HH:MM:SS'
            except ValueError:
                try:
                    pub_date = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %Z')  # RFC 822 형식
                except ValueError:
                    print(f"날짜 형식 오류: {pub_date}")
                    continue

        # 마지막 크롤링된 날짜와 비교
        if pub_date <= last_crawled_date:
            continue

        if link.startswith("/"):
            link = f"{base_domain}{link}"

        content, image_url = content_croll(link)

        # 이미 저장된 링크인지 확인
        cursor.execute("SELECT COUNT(*) FROM swpre WHERE link = %s", (link,))
        if cursor.fetchone()[0] > 0:
            continue

        # MySQL 테이블에 저장
        sql = "INSERT INTO swpre (title, link, content, image, date) VALUES (%s, %s, %s, %s, %s)"
        val = (title, link, content, image_url, pub_date)
        cursor.execute(sql, val)
        db.commit()

        # 저장된 데이터 출력
        print(f"제목: {title}")
        print(f"링크: {link}")
        print(f"내용: {content[:100]}...")  # 내용의 앞 100자만 출력
        print(f"이미지 URL: {image_url}")
        print(f"게시 날짜: {pub_date}")
        print("-" * 40)

        count += 1

        # 가장 오래된 새 공지사항 날짜 업데이트
        if oldest_new_date is None or pub_date < oldest_new_date:
            oldest_new_date = pub_date

# MySQL 연결 종료
cursor.close()
db.close()

# 가장 오래된 새 공지사항 날짜 출력
if oldest_new_date:
    print(f"가장 처음 저장된 새 공지사항 날짜: {oldest_new_date}")

print(f"새로운 공지사항 {count}개가 성공적으로 저장되었습니다.")
