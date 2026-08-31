# create_vector_db.py
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from document_chunking import ai_chunks, insurance_chunks

# .env 파일에서 환경 변수를 로드한다.
load_dotenv()

# 임베딩 모델을 설정합니다. 
embedding_model = OpenAIEmbeddings(model='text-embedding-3-small')

# 1. 두 청크 데이터를 하나로 합칩니다.
all_chunks = ai_chunks + insurance_chunks

# 2. Chroma DB를 생성하고 영구적으로 저장할 경로를 설정합니다.
persist_directory = 'chroma_data_db'

# 3. Chroma DB 생성 및 저장(실행 시간이 다소 걸릴 수 있습니다.)
vectorstore = Chroma.from_documents(
    documents=all_chunks,
    embedding=embedding_model,
    persist_directory=persist_directory
)