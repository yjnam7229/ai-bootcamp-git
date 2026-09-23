"""OpenDART 재무 조회와 PDF 보고서 생성을 제공하는 stdio MCP 서버."""

from app.mcp_tools import mcp


if __name__ == "__main__":
    mcp.run(transport="stdio")
