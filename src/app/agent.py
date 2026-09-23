"""
app/agent.py
------------
LangGraph 기반의 Agent 오케스트레이션 모듈.
사용자의 요청을 받아 mcp_tools를 호출할지, 답변을 생성할지 결정하는 상태 머신을 구축합니다.
"""

from typing import Annotated, Sequence, TypedDict
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from app.mcp_tools import ALL_SALES_TOOLS

# 환경 변수 로드
load_dotenv()


# 1. Agent의 상태(state) 스키마 정의
class AgentState(TypedDict):
    """
    messages: 대화 기록 및 Tool 호출 메세지 목록
    add_messages 리듀서를 사용해 기존 메시지에 새 메시지를 누적합니다.
    """
    messages: Annotated[Sequence[BaseMessage], add_messages]


# 2. LLM 초기화 및 Tool 바인딩
llm = ChatOpenAI(model="gpt-5-nano", temperature=0)
llm_with_tools = llm.bind_tools(ALL_SALES_TOOLS, parallel_tool_calls=False)

# 3. System Prompt 정의
SYSTEM_PROMPT = """
당신은 B2B 영업 제안서 작성을 지원하는 전문 에이전트 'SalesGPT'입니다.
제공된 도구(DART 재무 정보 조회, B2B 제안서 지식 베이스 검색)를 적극적으로 활용하여 정확하고 전문적인 제안서 문맥을 구성하세요.

- 기업 재무 상태나 실적 정보가 필요하면 `search_company_financials` 도구를 사용하세요.
- 제안서 템플릿, 보안 규정, 아키텍처 문맥이 필요하면 `query_proposal_knowledge_base` 도구를 사용하세요.
- 답변은 전문적이고 명확한 B2B 비즈니스 톤을 유지하세요.
"""


# 4. Agent 노드 함수 정의
def call_model_node(state: AgentState) -> dict:
    """LLM이 현재 상태를 판단하여 답변을 생성하거나 Tool 호출을 결정하는 노드"""

    messages = state["messages"]

    # System Message가 없다면 LLM 입력용 리스트 맨 앞에만 임시 추가
    if not any(isinstance(m, SystemMessage) for m in messages):
        prompt_messages = [SystemMessage(content=SYSTEM_PROMPT)] + list(messages)
    else:
        prompt_messages = messages

    # LLM이 질문을 보고 등록된 도구 목록(ALL_SALES_TOOLS) 중 어떤 도구를 호출할지 판단하여 tool_calls를 생성
    response = llm_with_tools.invoke(prompt_messages)

    # LLM이 선택한 도구 출력
    # print('LLM이 선택한 도구  ', response.tool_calls)

    return {"messages": [response]}


# 5. 조건부 분기 logic
def should_continue(state: AgentState) -> str:
    """LLM의 마지막 응답에 tool_calls가 포함되어 있는지 판단하는 조건부 에지(Edge)"""
    last_message = state["messages"][-1]

    # Tool 호출 요청이 있는 경우 'tools' 노드 이름 직접 반환
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    # Tool 호출이 없으면 종료
    return END


# 6. LangGraph 상태 머신 그래프 구성
def create_sales_agent_graph():
    """LangGraph 워크플로우를 생성하고 컴파일합니다."""
    workflow = StateGraph(AgentState)

    # 1. 노드 추가
    workflow.add_node("agent", call_model_node)
    workflow.add_node("tools", ToolNode(ALL_SALES_TOOLS))

    # 2. 에지 연결
    workflow.add_edge(START, "agent")

    # 조건부 에지 (should_continue 반환값인 'tools' 또는 END로 직접 이동)
    workflow.add_conditional_edges(
        "agent",
        should_continue
    )

    # 3. 도구 실행 후 다시 agent 노드로 순환
    workflow.add_edge("tools", "agent")

    # 4. 컴파일 후 전달
    return workflow.compile()


# 외부에서 호출 가능한 인스턴스 생성
sales_agent = create_sales_agent_graph()