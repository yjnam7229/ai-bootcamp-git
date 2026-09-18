import asyncio

from config import (
    DB_PATH,
    MODEL_NAME,
    TEMPERATURE,
    SYSTEM_PROMPT,
    MCP_SERVERS,
)

from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_community.tools import YouTubeSearchTool


# ============================================================
# Agent 전체 실행
# ============================================================

async def execute_agent(query: str, thread_id: str):
    """
    SQLite → MCP → Agent → 실행 → 리소스 정리
    전체 lifecycle을 하나의 asyncio 실행 안에서 관리합니다.
    """

    try:
        # ----------------------------------------------------
        # SQLite Checkpointer
        # ----------------------------------------------------

        async with AsyncSqliteSaver.from_conn_string(
            DB_PATH
        ) as checkpointer:

            # ------------------------------------------------
            # MCP Client
            # ------------------------------------------------

            client = MultiServerMCPClient(MCP_SERVERS)

            mcp_tools = await client.get_tools()

            # ------------------------------------------------
            # 일반 Tool
            # ------------------------------------------------

            youtube_tool = YouTubeSearchTool()

            all_tools = mcp_tools + [youtube_tool]

            # ------------------------------------------------
            # LLM
            # ------------------------------------------------

            model = ChatOpenAI(
                model=MODEL_NAME,
                temperature=TEMPERATURE,
            )

            # ------------------------------------------------
            # Agent
            # ------------------------------------------------

            agent = create_agent(
                model=model,
                checkpointer=checkpointer,
                tools=all_tools,
                system_prompt=SYSTEM_PROMPT,
            )

            # ------------------------------------------------
            # Agent 실행
            # ------------------------------------------------

            return await run_agent(
                agent=agent,
                query=query,
                thread_id=thread_id,
            )

    except asyncio.CancelledError:
        print("\n[SHUTDOWN] Agent task cancelled.")
        raise


# ============================================================
# Agent Streaming
# ============================================================

async def run_agent(
    agent,
    query: str,
    thread_id: str,
):
    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    full_response = ""

    try:
        async for chunk in agent.astream(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": query,
                    }
                ]
            },
            config=config,
            stream_mode="values",
        ):
            if "messages" not in chunk:
                continue

            messages = chunk["messages"]

            if not messages:
                continue

            latest_msg = messages[-1]

            print(latest_msg)

            if latest_msg.__class__.__name__ != "AIMessage":
                continue

            content = latest_msg.content

            if not content:
                continue

            finish_reason = (
                latest_msg.response_metadata.get(
                    "finish_reason"
                )
            )

            if finish_reason == "tool_calls":
                continue

            full_response = content

    except asyncio.CancelledError:
        print("\n[SHUTDOWN] Streaming cancelled.")
        raise

    return full_response
