import asyncio
import os

from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient


SLACK_MCP_URL = "https://mcp.slack.com/mcp"


async def main():
    load_dotenv()

    slack_token = os.getenv("SLACK_USER_TOKEN")
    channel_id = os.getenv("SLACK_CHANNEL_ID")

    if not slack_token:
        raise RuntimeError(
            "SLACK_USER_TOKEN이 없습니다. "
            ".env 파일을 확인해주세요."
        )

    if not channel_id:
        raise RuntimeError(
            "SLACK_CHANNEL_ID가 없습니다. "
            ".env 파일을 확인해주세요."
        )

    print("1. 환경변수 확인: OK")
    print("2. Slack MCP 연결 시도...")

    client = MultiServerMCPClient(
        {
            "slack": {
                "transport": "streamable_http",
                "url": SLACK_MCP_URL,
                "headers": {
                    "Authorization": f"Bearer {slack_token}"
                },
            }
        }
    )

    try:
        # Slack MCP Tool 조회
        tools = await client.get_tools(server_name="slack")

        print("3. Slack MCP 연결 성공")
        print(f"4. Tool 개수: {len(tools)}")

        # slack_send_message 찾기
        send_tool = next(
            (
                tool
                for tool in tools
                if tool.name == "slack_send_message"
            ),
            None,
        )

        if send_tool is None:
            raise RuntimeError(
                "slack_send_message Tool을 찾을 수 없습니다."
            )

        print("5. slack_send_message Tool 확인: OK")
        print("6. 테스트 메시지 전송...")

        result = await send_tool.ainvoke(
            {
                "channel_id": channel_id,
                "message": "재무분석 챗봇 Slack MCP 연결 테스트"
            }
        )

        print()
        print("===== Slack MCP 전송 결과 =====")
        print(result)
        print("==============================")
        print()
        print("Slack MCP 메시지 전송 완료")

    except Exception as exc:
        print()
        print("Slack MCP 테스트 실패")
        print(f"오류 유형: {type(exc).__name__}")
        print(f"오류 내용: {exc}")
        raise


if __name__ == "__main__":
    asyncio.run(main())