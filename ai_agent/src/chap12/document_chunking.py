from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 1. AI 용어 로드(텍스트 파일)
ai_loader = TextLoader("./data/Python_AI_Glossary_Guide.txt", encoding="utf-8")
ai_docs = ai_loader.load()

# 2. 펫보험 약관 로드(PDF 파일)
insurance_loader = PyPDFLoader("./data/meritz_pet_insurance.pdf")
insurance_docs = insurance_loader.load()

# 청킹 설정: 200자씩 자르고, 20자는 겹치게(overlap) 설정
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 200,
    chunk_overlap = 20
)

# AI 용어 청킹
ai_chunks = text_splitter.split_documents(ai_docs)

# 펫보험 청킹
insurance_chunks = text_splitter.split_documents(insurance_docs)

# 1. AI 용어 청크에 메타데이터 추가
for chunk in ai_chunks:
    chunk.metadata["source_type"] = "glossary"
    chunk.metadata["category"] = "AI & Python"

for chunk in insurance_chunks:
    chunk.metadata["source_type"] = "insurance"
    chunk.metadata["category"] = "Pet Insurance"
