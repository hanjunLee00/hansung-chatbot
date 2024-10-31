#pinecone 벡터 데이터베이스 내용 지우기 테스트

from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from dotenv import load_dotenv

embedding = OpenAIEmbeddings(model='text-embedding-3-large')
index_name = 'crawled-db-ver2'

