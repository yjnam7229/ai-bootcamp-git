# retriever_serch.py
# 저장된 벡터 저장소 불러오기와 Retriever 객체 생성

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

# 임베딩 모델을 설정합니다. 
embedding_model = OpenAIEmbeddings(model='text-embedding-3-small')

# 1. 저장된 벡터 데이터베이스를 다시 불러옵니다. (생성이 아님!)
retrieved_vectorstore = Chroma(
    persist_directory="chroma_data_db",
    embedding_function=embedding_model # 4절에서 설정한 모델 사용
)

collection = retrieved_vectorstore.get()
print(f"총 {len(collection['ids'])}개 문서 확인.")

# 3.2 '검색(Retriever)' 객체를 생성합니다.
# retriever = retrieved_vectorstore.as_retriever()

# 3.1 필터 조건 설정합니다. (새롭게 추가된 부분)
ai_fliter = {
    # 'source_type': 'glossary',    # 팻 보험 청크는 제외하는 메타데이터 추가
    'source_type': 'insurance',
}

retriever = retrieved_vectorstore.as_retriever(
    search_kwargs={
        'filter': ai_fliter
    },
)

# 4. 검색어를 사용하여 문서를 검색합니다.
query = '보험 약관 정리해 줘.'
# query = '원본 데이터 정제(Cleaning) 단계를 보완 해서 보험 약관 정리해 줘.'

# query = '파이썬 반복문에 대해 알려줘.'

docs = retriever.invoke(query)
print(f'검색 결과 문서 수 {len(docs)}개')

# 어떤 chunk 데이터를 검색 하고 있는지 확인
for i in range(len(docs)):
    print(f"\n--- 문서 {i+1} ---")
    print(docs[i].page_content)

# 5. 검색 타입을 'mmr'로 변경하여 새로운 retriever를 생성합니다.
mmr_retriever = retrieved_vectorstore.as_retriever(
    search_type='mmr',
    search_kwargs={
        'k': 5,          # default 값은 4
        'fetch_k': 20,   # 1차적으로 빠르게 20개 검색된 결과를 가져와서 5개을 선택(k:5) 
        'filter': ai_fliter
    }
)
# 6. MMR 검색 수행
mmr_query = '보험 약관 정리해 줘.'
# mmr_query = '원본 데이터 정제(Cleaning) 단계를 보완 해서 보험 약관 정리해 줘.'

mmr_docs = mmr_retriever.invoke(mmr_query)

print(f'MMR 검색 결과 문서 수 {len(mmr_docs)}개')

for i in range(len(mmr_docs)):
    print(f"\n--- 문서 {i+1} ---")
    print(mmr_docs[i].page_content)


