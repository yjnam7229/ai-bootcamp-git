"""재무 상담 LangGraph 에이전트와 MCP 서버 연결."""

from __future__ import annotations

import os
import sys
from functools import partial
from pathlib import Path
from time import perf_counter
from typing import Annotated, Any, Sequence, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

_SRC_DIR = Path(__file__).resolve().parents[1]
_PROJECT_ROOT = _SRC_DIR.parent
load_dotenv(_PROJECT_ROOT / ".env")
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from app.prompts import build_financial_system_prompt

# PERF_LOG = Path(_SRC_DIR) / "agent_perf.log"
PERF_LOG = Path(_SRC_DIR) / "streamlit_perf.log"

def _perf_log(message: str) -> None:
    with PERF_LOG.open("a", encoding="utf-8") as f:
        print(message, file=f, flush=True)


class AgentState(TypedDict):
    """LangGraph가 대화와 도구 실행 메시지를 누적하는 상태."""

    messages: Annotated[Sequence[BaseMessage], add_messages]


# 아래 `_` 접두사 함수들은 이 모듈의 그래프 구성에만 쓰이는 내부 구현이다.
def _call_model_node(
    state: AgentState,
    *,
    system_prompt: str,
    tool_llm_with_tools: Any,
    answer_llm_with_tools: Any,
) -> dict[str, list[BaseMessage]]:
    """도구 선택과 최종 답변의 reasoning 수준을 분리해 모델을 호출한다."""
    messages = list(state["messages"])

    if not messages or not isinstance(messages[0], SystemMessage):
        messages.insert(0, SystemMessage(content=system_prompt))

    # ToolMessage가 있으면 OpenDART 조회 이후의 최종 답변 단계다.
    is_answer_phase = any(isinstance(message, ToolMessage) for message in messages)
    phase = "answer" if is_answer_phase else "tool_selection"
    llm_with_tools = (
        answer_llm_with_tools if is_answer_phase else tool_llm_with_tools
    )

    message_chars = sum(
        len(str(getattr(message, "content", "") or ""))
        for message in messages
    )

    _perf_log(
        f"[PERF-AGENT] LLM input: "
        f"phase={phase}, "
        f"messages={len(messages)}, "
        f"chars={message_chars:,}"
    )

    started = perf_counter()

    try:
        response = llm_with_tools.invoke(messages)

        output_content = getattr(response, "content", "") or ""
        output_chars = len(str(output_content))
        usage = getattr(response, "usage_metadata", None)

        _perf_log(
            f"[PERF-AGENT] LLM output: "
            f"phase={phase}, "
            f"chars={output_chars:,}, "
            f"usage={usage}"
        )

        return {"messages": [response]}

    finally:
        _perf_log(
            f"[PERF-AGENT] LLM invoke: "
            f"phase={phase}, "
            f"{perf_counter() - started:.3f}s"
        )


def _should_continue(state: AgentState) -> str:
    """마지막 모델 응답에 도구 호출이 있으면 도구 노드로 보낸다."""
    last_message = state["messages"][-1]
    return "tools" if getattr(last_message, "tool_calls", None) else END


def _compile_agent(system_prompt: str, tools: Sequence[object]):
    """도구 선택과 재무 답변의 reasoning 수준을 분리한 LangGraph를 만든다."""
    model_name = os.getenv("DEFAULT_LLM_MODEL", "gpt-5-nano")

    # 1차 호출: 어떤 MCP 도구를 호출할지만 결정한다.
    # 재무 계산/해석 단계가 아니므로 reasoning을 최소화한다.
    tool_llm = ChatOpenAI(
        model=model_name,
        reasoning_effort=os.getenv("TOOL_REASONING_EFFORT", "minimal"),
    )

    # 2차 호출: OpenDART 결과를 근거로 최종 재무 답변을 작성한다.
    # 정확성을 위해 reasoning을 완전히 끄지 않고 low를 기본값으로 둔다.
    answer_llm = ChatOpenAI(
        model=model_name,
        reasoning_effort=os.getenv("ANSWER_REASONING_EFFORT", "low"),
    )

    tool_llm_with_tools = tool_llm.bind_tools(
        list(tools),
        parallel_tool_calls=False,
    )
    answer_llm_with_tools = answer_llm.bind_tools(
        list(tools),
        parallel_tool_calls=False,
    )

    workflow = StateGraph(AgentState)
    workflow.add_node(
        "agent",
        partial(
            _call_model_node,
            system_prompt=system_prompt,
            tool_llm_with_tools=tool_llm_with_tools,
            answer_llm_with_tools=answer_llm_with_tools,
        ),
    )
    workflow.add_node("tools", ToolNode(list(tools)))
    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", _should_continue)
    workflow.add_edge("tools", "agent")
    return workflow.compile()


async def create_financial_agent_graph(understanding_level: str):
    """stdio MCP 서버에서 도구를 읽어 이해 수준별 재무 상담 그래프를 만든다."""
    system_prompt = build_financial_system_prompt(understanding_level)
    minimal_env = {
        "PATH": os.environ.get("PATH", ""),
        "PYTHONPATH": str(_SRC_DIR),
        "PYTHONUNBUFFERED": "1",
    }
    mcp_client = MultiServerMCPClient(
        {
            "opendart_financial": {
                "transport": "stdio",
                "command": sys.executable,
                "args": ["-m", "app.mcp_server"],
                "cwd": str(_SRC_DIR),
                "env": minimal_env,
            }
        }
    )
    started = perf_counter()
    tools = await mcp_client.get_tools()
    _perf_log(f"[PERF-AGENT] MCP get_tools: {perf_counter() - started:.3f}s")
    if not tools:
        raise RuntimeError("재무 MCP 서버에서 사용 가능한 도구를 찾지 못했습니다.")

    started = perf_counter()
    graph = _compile_agent(system_prompt, tools)
    _perf_log(f"[PERF-AGENT] compile_agent: {perf_counter() - started:.3f}s")
    return graph
