"""
app/agent.py
------------
LangGraph 기반의 Agent 오케스트레이션 모듈.
사용자의 요청을 받아 mcp_tools를 호출할지, 답변을 생성할지 결정하는 상태 머신을 구축합니다.
"""

from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from app.mcp_tools import ALL_SALES_TOOLS


# 1. Agent의 상태(State) 스키마 정의
class AgentState(TypedDict):
    """
    messages: 대화 기록 및 Tool 호출 메세지 목록.
    add_messages 리듀서를 사용해 기존 메시지에 새 메시지를 누적합니다.
    """
    messages: Annotated[Sequence[BaseMessage], add_messages]


# 2. LLM 초기화 및 Tool 바인딩
# OpenAI gpt-4o 또는 gpt-4o-mini 모델 활용
llm = ChatOpenAI(model="gpt-4o", temperature=0.2)
llm_with_tools = llm.bind_tools(ALL_SALES_TOOLS)


# 3. System Prompt 정의
SYSTEM_PROMPT = """
당신은 B2B 영업 제안서 작성을 지원하는 전문 에이전트 'SalesGPT'입니다.
제공된 도구(DART 재무 정보 조회, B2B 제안서 지식 베이스 검색)를 적극적으로 활용하여 정확하고 전문적인 제안서 문맥을 구성하세요.

- 기업 재무 상태나 실적 정보가 필요하면 `search_company_financials` 도구를 사용하세요.
- 제안서 템플릿, 보안 규정, 아키텍처 문맥이 필요하면 `query_proposal_knowledge_base` 도구를 사용하세요.
- 답변은 전문적이고 명확한 B2B 비즈니스 톤을 유지하세요.
"""


# 4. Agent 노드 함수 정의
def agent_node(state: AgentState) -> dict:
    """LLM이 현재 상태를 판단하여 답변을 생성하거나 Tool 호출을 결정하는 노드"""
    messages = state["messages"]
    
    # System Message가 없는 경우 맨 앞에 추가
    if not any(isinstance(m, SystemMessage) for m in messages):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + list(messages)
        
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


# 5. 조건부 분기 logic (Should Continue)
def should_continue(state: AgentState) -> str:
    """LLM의 마지막 응답에 tool_calls가 포함되어 있는지 판단하는 조건부 에지"""
    last_message = state["messages"][-1]
    
    # Tool 호출 요청이 있는 경우 'tools' 노드로 이동
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    # Tool 호출이 없으면 종료 (END)
    return END


# 6. LangGraph 상태 머신 그래프 구성
def create_sales_agent_graph():
    """LangGraph 워크플로우를 생성하고 컴파일합니다."""
    workflow = StateGraph(AgentState)

    # 노드 등록
    workflow.add_node("agent", agent_node)
    
    # LangGraph 전용 prebuilt ToolNode 사용 (mcp_tools 자동 실행)
    tool_node = ToolNode(ALL_SALES_TOOLS)
    workflow.add_node("tools", tool_node)

    # 진입점(Entry Point) 설정
    workflow.set_entry_point("agent")

    # 조건부 에지 추가: agent -> (tools 또는 END)
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            END: END,
        },
    )

    # 순환 에지 추가: tools -> agent (Tool 실행 결과를 다시 agent에게 전달)
    workflow.add_edge("tools", "agent")

    # 그래프 컴파일
    return workflow.compile()


# 외부에서 호출 가능한 인스턴스
sales_agent = create_sales_agent_graph()