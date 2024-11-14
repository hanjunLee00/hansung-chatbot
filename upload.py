import mysql.connector
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from dotenv import load_dotenv

load_dotenv()

class Document:
    def __init__(self, page_content, metadata=None, id=None):
        self.page_content = page_content
        self.metadata = metadata if metadata is not None else {}
        self.id = id

# Step 1: MySQL에 연결
db = mysql.connector.connect(
    host="localhost",        
    user="root",            
    password="12345678",    
    database="crawled"      
)

cursor = db.cursor()

# Step 2: 테이블에서 추출된 데이터를 배열로 반환
def crawled_data_to_array():
    fetch_query = "SELECT id, title, link, content, date FROM swpre"
    cursor.execute(fetch_query)
    rows = cursor.fetchall()
    return rows

# Step 3: 메타데이터와 함께 임베딩 생성 및 저장
def store_array_to_vector_db():
    embedding = OpenAIEmbeddings(model='text-embedding-3-large')
    index_name = 'crawled-db-ver2'

    rows = crawled_data_to_array()
    documents = []
    for id, title, link, content, pub_date in rows:
        # 메타데이터를 포함하여 문서 내용을 생성합니다.
        combined_content = f"Title: {title}\nLink: {link}\nDate: {pub_date}\nContent: {content}"
        metadata = {'title': title, 'link': link, 'date': pub_date}
        documents.append(Document(combined_content, metadata, id=str(id)))

    # 문서를 Pinecone에 저장합니다.
    database = PineconeVectorStore.from_documents(documents, embedding, index_name=index_name)

store_array_to_vector_db()

cursor.close()
db.close()
