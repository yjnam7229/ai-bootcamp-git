# app/agent.py
"""
LangGraph 기반의 Agent 오케스트레이션 모듈.
사용자의 요청을 받아 mcp_tools를 호출할지, 답변을 생성할지 결정하는 상태 머신을 구축합니다.
"""
import os
import sqlite3
import logging
from typing import Annotated, Sequence, TypedDict, Optional

from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.sqlite import SqliteSaver

from mcp_tools import ALL_SALES_TOOLS
from config import settings

# 로깅 설정
logger = logging.getLogger(__name__)

# 환경 변수 로드
load_dotenv()

# 1. DB 저장 디렉토리 및 SQLite DB 연결 설정
checkpointer_path = str(settings.CHECKPOINT_DB_PATH)
# 파일이 아닌 '상위 디렉토리'를 생성해야 함
os.makedirs(os.path.dirname(checkpointer_path), exist_ok=True)

conn = sqlite3.connect(checkpointer_path, check_same_thread=False)
checkpointer = SqliteSaver(conn)


# 2. Agent의 상태(state) 스키마 정의
class AgentState(TypedDict):
    """
    messages: 대화 기록 및 Tool 호출 메세지 목록
    add_messages 리듀서를 사용해 기존 메시지에 새 메시지를 누적합니다.
    """
    messages: Annotated[Sequence[BaseMessage], add_messages]


# 3. LLM 초기화 및 Tool 바인딩
llm = ChatOpenAI(model="gpt-5-nano", temperature=0)
llm_with_tools = llm.bind_tools(ALL_SALES_TOOLS, parallel_tool_calls=False)

# 4. System Prompt 정의
SYSTEM_PROMPT = """
당신은 B2B 영업 제안서 작성을 지원하는 전문 에이전트 'SalesGPT'입니다.
제공된 도구(DART 재무 정보 조회, B2B 제안서 지식 베이스 검색)를 적극적으로 활용하여 정확하고 전문적인 제안서 문맥을 구성하세요.

- 기업 재무 상태나 실적 정보가 필요하면 `search_company_financials` 도구를 사용하세요.
- 제안서 템플릿, 보안 규정, 아키텍처 문맥이 필요하면 `query_proposal_knowledge_base` 도구를 사용하세요.
- 답변은 전문적이고 명확한 B2B 비즈니스 톤을 유지하세요.
"""

# 5. Agent 노드 함수 정의 
def call_model_node(state: AgentState) -> dict:
    """LLM이 현재 상태를 판단하여 답변을 생성하거나 Tool 호출을 결정하는 노드"""
    messages = state["messages"]

    # System Message가 없다면 LLM 입력용 리스트 맨 앞에만 임시 추가
    if not any(isinstance(m, SystemMessage) for m in messages):
        prompt_messages = [SystemMessage(content=SYSTEM_PROMPT)] + list(messages)
    else:
        prompt_messages = messages

    response = llm_with_tools.invoke(prompt_messages)
    return {"messages": [response]}


# 6. 조건부 분기 logic
def should_continue(state: AgentState) -> str:
    """LLM의 마지막 응답에 tool_calls가 포함되어 있는지 판단하는 조건부 에지(Edge)"""
    last_message = state["messages"][-1]

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END


# 7. LangGraph 상태 머신 그래프 구성
def create_sales_agent_graph():
    """LangGraph 워크플로우를 생성하고 컴파일합니다."""
    workflow = StateGraph(AgentState)

    workflow.add_node("agent", call_model_node)
    workflow.add_node("tools", ToolNode(ALL_SALES_TOOLS))

    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", should_continue)
    workflow.add_edge("tools", "agent")

    # SqliteSaver를 체크포인터로 등록
    return workflow.compile(checkpointer=checkpointer)


# 외부에서 호출 가능한 인스턴스 생성
sales_agent = create_sales_agent_graph()


# 8. main.py(Streamlit UI) 전용 실행 진입점 함수
def run_sales_agent(
    company_name: str, 
    stock_code: str, 
    additional_requirements: Optional[str] = None,
    thread_id: str = "session_001"
) -> str:
    """
    main.py에서 직접 호출하는 함수입니다.
    SqliteSaver 체크포인터가 지정되어 있으므로 thread_id별로 세션 상태가 보존됩니다.
    """
    logger.info(f"[{company_name}] SalesGPT 에이전트 실행 (Thread ID: {thread_id})")

    user_prompt = (
        f"기업명: {company_name}\n"
        f"종목코드/고유번호: {stock_code}\n"
        f"추가 요구사항: {additional_requirements or '없음'}\n\n"
        f"위 정보를 바탕으로 DART 재무 데이터를 조회하고 ChromaDB RAG 지식을 활용하여 "
        f"맞춤형 B2B 클라우드 전환 제안서를 작성해 주세요."
    )

    initial_state = {"messages": [("user", user_prompt)]}
    config = {"configurable": {"thread_id": thread_id}}

    try:
        final_state = sales_agent.invoke(initial_state, config=config)
        last_message = final_state["messages"][-1]
        return getattr(last_message, "content", str(last_message))
    except Exception as e:
        logger.error(f"에이전트 실행 중 오류 발생: {e}", exc_info=True)
        raise e