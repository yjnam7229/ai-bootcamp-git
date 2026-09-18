from pathlib import Path

from mcp.server.fastmcp import FastMCP


# ============================================================
# MCP 서버
# ============================================================

mcp = FastMCP("file-server")


# ============================================================
# 파일 저장 디렉토리
# ============================================================

BASE_DIR = (
    Path(__file__).resolve().parent.parent
    / "output"
)

BASE_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# Markdown 저장 Tool
# ============================================================

@mcp.tool(
    "write_markdown",
    description=(
        "content의 키워드를 파일명으로 하여 "
        "지정된 경로에 내용을 마크다운 파일로 저장합니다."
    ),
)
def write_markdown(
    path: str,
    content: str,
):
    """
    Markdown 파일을 output 디렉토리에 저장합니다.
    """

    try:
        filename = Path(path).name
        target = BASE_DIR / filename

        target.write_text(
            content,
            encoding="utf-8",
        )

        return (
            f"Successfully wrote to '{filename}'"
        )

    except Exception as e:

        return (
            "Error: 파일 저장 중에 오류가 발생했습니다. "
            f"{str(e)}"
        )


# ============================================================
# MCP 서버 실행
# ============================================================

if __name__ == "__main__":
    mcp.run(
        transport="stdio"
    )
