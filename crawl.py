import requests
from bs4 import BeautifulSoup as bs
import pymysql  # pymysql로 변경

# 공지사항 내용을 크롤링하는 함수
def content_croll(url):
    page = requests.get(url)
    soup = bs(page.text, 'html.parser')
    view_con_div = soup.find('div', class_='view-con')
    
    content = ""
    image_url = None
    if view_con_div:
        content = view_con_div.get_text(strip=True)
        
        # 이미지 URL을 찾기 (content와 상관없이 이미지 URL을 추출)
        image_tag = view_con_div.find('img')
        if image_tag and 'src' in image_tag.attrs:
            image_url = image_tag['src']
    
    else:
        content = "No content found"
    
    return content, image_url

# MySQL 연결 설정
db = pymysql.connect(
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

# 최신 공지사항 페이지 순회
base_url = 'https://www.hansung.ac.kr/bbs/hansung/143/rssList.do?page={}'

for page_number in range(1, 92):
    url = base_url.format(page_number)
    page = requests.get(url)
    soup = bs(page.text, 'xml')
    articles = soup.find_all('item')
    base_domain = "https://www.hansung.ac.kr"

    for article in articles:
        title = article.find('title').get_text(strip=True) if article.find('title') else "No Title"
        link = article.find('link').get_text() if article.find('link') else "No Link"
        pub_date = article.find('pubDate').get_text(strip=True) if article.find('pubDate') else "No Date"

        if link.startswith("/"):
            link = f"{base_domain}{link}"

        content, image_url = content_croll(link)

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
        print("-" * 40)  # 구분선 출력

# MySQL 연결 종료
cursor.close()
db.close()

print("모든 공지사항이 성공적으로 저장되었습니다.")
