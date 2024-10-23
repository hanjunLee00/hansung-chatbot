import mysql.connector
from pinecone import Pinecone
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore

load_dotenv()

# Step 1: MySQL에 연결
db = mysql.connector.connect(
    host="localhost",        # MySQL 호스트 (예: 'localhost')
    user="root",            # MySQL 사용자 이름
    password="12345678",    # MySQL 비밀번호
    database="crawled"      # 데이터베이스 이름
)

cursor = db.cursor()

# 연결된 테이블에서 배열로 저장 ex(id, title) 형식
def crawled_data_to_array():
    fetch_query = "SELECT id, title, content, pubDate FROM swfree"
    cursor.execute(fetch_query)
    rows = cursor.fetchall()
    return rows

# 데이터를 Pinecone에 저장
def store_array_to_PCVS():

    embedding = OpenAIEmbeddings(model='text-embedding-3-large')
    index_name = 'crawled-db'

    # MySQL에서 데이터를 가져옴
    rows = crawled_data_to_array()

    # 문서 형식으로 변환
    documents = []
    for id, title in rows:
        documents.append({'id': id, 'text': title})

    len(documents)

    # PineconeVectorStore에 저장
    database = PineconeVectorStore.from_documents(documents, embedding, index_name=index_name)

# 실행
store_array_to_PCVS()
