from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from mcp.server.fastmcp import FastMCP


# ============================================================
# 환경변수
# ============================================================

load_dotenv()


# ============================================================
# MCP 서버
# ============================================================

mcp = FastMCP("wine-rag-server")


# ============================================================
# Vector DB 경로
# ============================================================

DB_PATH = (
    Path(__file__).resolve().parent.parent
    / "vector_store"
    / "wine_db"
)


# ============================================================
# Vector Store
# ============================================================

_vector_store = None


def get_vector_store():
    """
    실제 검색 요청 시 Vector Store를 생성하고,
    이후에는 생성된 객체를 재사용합니다.
    """

    global _vector_store

    if _vector_store is None:

        embedding_model = OpenAIEmbeddings(
            model="text-embedding-3-small"
        )

        _vector_store = Chroma(
            persist_directory=str(DB_PATH),
            embedding_function=embedding_model,
        )

    return _vector_store


# ============================================================
# Wine RAG 검색 Tool
# ============================================================

@mcp.tool(
    "search_wine",
    description=(
        "와인 정보를 벡터 검색으로 조회합니다. "
        "source_type: Structured Data, "
        "Unstructured Data, all 지원"
    ),
)
def search_wine(
    query: str,
    source_type: str = "all",
    k: int = 3,
):
    """
    와인 RAG 검색

    source_type:
        Structured Data
        Unstructured Data
        all
    """

    # --------------------------------------------------------
    # 검색 개수 제한
    # --------------------------------------------------------

    k = max(1, min(k, 10))

    # --------------------------------------------------------
    # Filter
    # --------------------------------------------------------

    if source_type == "all":
        filter_dict = None
    else:
        filter_dict = {
            "source_type": source_type
        }

    # --------------------------------------------------------
    # Vector Store
    # --------------------------------------------------------

    vector_store = get_vector_store()

    # --------------------------------------------------------
    # Retriever
    # --------------------------------------------------------

    retriever = vector_store.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": k,
            "fetch_k": 15,
            "lambda_mult": 0.6,
            "filter": filter_dict,
        },
    )

    # --------------------------------------------------------
    # 검색
    # --------------------------------------------------------

    results = retriever.invoke(query)

    if not results:
        return "검색 결과가 없습니다."

    return results


# ============================================================
# MCP 서버 실행
# ============================================================

if __name__ == "__main__":
    mcp.run(
        transport="stdio"
    )
