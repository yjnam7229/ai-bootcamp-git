# vector.py

import os
import logging
from typing import List, Optional

import chromadb
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    Document,
    Settings,
)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding

from app.config import settings

# 로깅 설정
logger = logging.getLogger(__name__)


class VectorStoreService:
    """LlamaIndex 및 Chroma DB 기반 비정형 문서 RAG 서비스"""

    def __init__(self, collection_name: str = "sales_proposal_kb"):
        self.collection_name = collection_name
        self.chroma_db_path = settings.CHROMA_DB_PATH  # 예: "data/chroma"

        # 1. Chroma DB 영속성 클라이언트 초기화
        os.makedirs(self.chroma_db_path, exist_ok=True)
        self.chroma_client = chromadb.PersistentClient(path=self.chroma_db_path)
        self.chroma_collection = self.chroma_client.get_or_create_collection(
            name=self.collection_name
        )

        # 2. LlamaIndex 전역 설정 (임베딩 모델 및 텍스트 분할기)
        Settings.embed_model = OpenAIEmbedding(
            model="text-embedding-3-small",
            api_key=settings.OPENAI_API_KEY
        )
        Settings.node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=50)

        # 3. Vector Store 및 Storage Context 바인딩
        self.vector_store = ChromaVectorStore(chroma_collection=self.chroma_collection)
        self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)

    def get_index(self) -> VectorStoreIndex:
        """기존 Chroma DB 수집본을 기반으로 LlamaIndex VectorStoreIndex를 로드합니다."""
        return VectorStoreIndex.from_vector_store(
            vector_store=self.vector_store,
            storage_context=self.storage_context,
        )

    def ingest_documents_from_directory(self, dir_path: str) -> int:
        """
        지정한 디렉토리 내의 문서(PDF, TXT, DOCX 등)를 읽어와 벡터 DB에 저장/인덱싱합니다.
        """
        if not os.path.exists(dir_path):
            logger.warning(f"문서 디렉토리가 존재하지 않습니다: {dir_path}")
            return 0

        try:
            # 문서 로드 (LlamaIndex SimpleDirectoryReader)
            reader = SimpleDirectoryReader(input_dir=dir_path, recursive=True)
            documents = reader.load_data()

            if not documents:
                logger.info(f"디렉토리에 로드할 문서가 없습니다: {dir_path}")
                return 0

            # 벡터 인덱스 생성 및 저장
            VectorStoreIndex.from_documents(
                documents,
                storage_context=self.storage_context,
                show_progress=True,
            )
            logger.info(f"문서 인덱싱 완료: 총 {len(documents)}개 문서 조각 저장됨.")
            return len(documents)

        except Exception as e:
            logger.error(f"문서 인덱싱 중 오류 발생: {e}")
            raise e

    def query_knowledge_base(self, query_str: str, similarity_top_k: int = 3) -> List[str]:
        """
        입력된 질의에 대해 지식 베이스(RAG)에서 가장 유사도가 높은 관련 문맥을 검색합니다.
        """
        try:
            index = self.get_index()
            retriever = index.as_retriever(similarity_top_k=similarity_top_k)
            nodes = retriever.retrieve(query_str)

            # 검색된 노드의 텍스트만 추출하여 반환
            contexts = [node.get_content() for node in nodes]
            logger.info(f"RAG 검색 완료: '{query_str}' (검색 결과 {len(contexts)}건)")
            return contexts

        except Exception as e:
            logger.error(f"RAG 검색 처리 중 오류 발생: {e}")
            return []


# 모듈 외부에서 쉽게 재사용할 수 있는 싱글톤/도우미 함수
def get_vector_service() -> VectorStoreService:
    return VectorStoreService()