# server.py
from mcp.server.mcpserver import MCPServer
# from mcp.server.fastmcp import FastMCP

mcp = MCPServer('MyServer')

# 별도의 descrption이 정의 안됨(doc string 내용이 에이전트의 descrption으로 전달)
@mcp.tool()
def summarize_text(text:str) -> str:    # string 타입으로 반환
    """긴 텍스트를 요약해 간결하게 반환합니다."""
    return text[:100] + '...'

# 이 파일이 직접 실행될 때 서버가 켜지도록 설정
# stdio : Standard I/O
if __name__ == '__main__':
    mcp.run(transport='streamable-http')  

# mcp.run(transport='streamable-http')가 핵심, 연결을 유지하면서 서버가 추후에 응답을 보내줌
# 이는 서버를 인터넷(HTTP)이 아닌, streamable-http 방식으로 실행하겠다는 뜻 
# 로컬에서 에이전트와 빠르고 안전하게 통신하기 위해 주로 사용되는 방식
