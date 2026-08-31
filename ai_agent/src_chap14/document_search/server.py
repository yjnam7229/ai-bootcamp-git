# llama 인덱스 라이브러리를 사용해서 문서를 불러오고, 벡터로 인덱싱 한 후 자연어 질문에 응답할 수 있는 검색엔진을 구성
# 문서 검색 에이전트 MCP
# 2개의 검색기(llama_query_engine, github_query_engine)를 어댑터를 이용해 MCP 서버에 툴로 등록
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from dotenv import load_dotenv

load_dotenv()

llama_docs = SimpleDirectoryReader("./llamaindex_docs").load_data()
llama_index = VectorStoreIndex.from_documents(llama_docs)
llama_query_engine = llama_index.as_query_engine()

github_docs = SimpleDirectoryReader("./github_docs").load_data()
github_index = VectorStoreIndex.from_documents(github_docs)
github_query_engine = github_index.as_query_engine()

from mcp.server.mcpserver import MCPServer

mcp = MCPServer("SearchServer")

@mcp.tool()
def seach_llama_docs(query: str) -> str:
    """llamaindex 문서에서 질의에 맞는 내용을 검색합니다."""
    return llama_query_engine.query(query).response

@mcp.tool()
def seach_github_docs(query: str) -> str:
    """깃허브 문서에서 질의에 맞는 내용을 검색합니다."""
    return github_query_engine.query(query).response

# 실행
if __name__ == "__main__":
    mcp.run(transport="streamable-http")

# bash쉘 :  python server.py 실행 -> MCP 서버 구동
# PowerShell 실행
# PS C:\WINDOWS\system32> mcp-inspector + ENTER 

# Starting MCP inspector...
# MCP Inspector Web is up and running at:
#    http://127.0.0.1:6274?MCP_INSPECTOR_API_TOKEN=63f557a9dce2dd144e76665d777a7e0182b3beb9ec1577bb9464f025f55ffc10
#    Sandbox (MCP Apps): http://127.0.0.1:6275/sandbox
#    Auth token: 63f557a9dce2dd144e76665d777a7e0182b3beb9ec1577bb9464f025f55ffc10
#    Secrets: OS keychain
# Opening browser...