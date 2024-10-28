import mysql.connector
from langchain_openai import OpenAIEmbeddings  # 수정된 임포트
from langchain_pinecone import PineconeVectorStore
from dotenv import load_dotenv

load_dotenv()

class Document:
    def __init__(self, page_content, metadata=None, id=None):
        self.page_content = page_content
        self.metadata = metadata if metadata is not None else {}
        self.id = id  # id 속성 추가

# Step 1: MySQL에 연결
db = mysql.connector.connect(
    host="localhost",        
    user="root",            
    password="12345678",    
    database="crawled"      
)

cursor = db.cursor()

def crawled_data_to_array():
    fetch_query = "SELECT id, title, link, content, date FROM swfree"
    cursor.execute(fetch_query)
    rows = cursor.fetchall()
    return rows

def store_array_to_PCVS():
    embedding = OpenAIEmbeddings(model='text-embedding-3-large')
    index_name = 'crawled-db-ver2'

    rows = crawled_data_to_array()
    documents = []
    for id, title, link, content, pub_date in rows:
        metadata = {'title': title, 'link': link, 'date': pub_date}
        documents.append(Document(content, metadata, id=str(id)))  # id를 문자열로 변환하여 전달

    database = PineconeVectorStore.from_documents(documents, embedding, index_name=index_name)
    print(f"{len(documents)} documents stored in Pinecone.")


store_array_to_PCVS()

cursor.close()
db.close()
