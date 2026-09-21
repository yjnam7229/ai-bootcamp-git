"""
test_runner.py
--------------
B2B SalesGPT Core 파이프라인 통합 테스트 스크립트.
"""

import os
from langchain_core.messages import HumanMessage
from app.config import engine, Base, SessionLocal
from app.dart import get_dart_service
from app.agent import sales_agent
from langchain_core.tracers import ConsoleCallbackHandler
from langchain_core.tracers.context import tracing_v2_enabled  # LangSmith 추적 URL 확인


def test_dart_caching_pipeline():
    print("\n==================================================")
    print(" 1. DART 정형 데이터 수집 및 DB 캐싱 테스트")
    print("==================================================")

    # DB 테이블 생성 (data/app.db)
    os.makedirs("./data", exist_ok=True)
    Base.metadata.create_all(bind=engine)

    dart_service = get_dart_service()
    db = SessionLocal()

    # 삼성전자 (corp_code: 00126380, 2023년)
    test_corp = "00126380"
    test_year = "2023"

    print("\n[1차 호출] API 수집 및 Pydantic 검증 -> SQLite DB 저장")
    res1 = dart_service.fetch_financial_data(corp_code=test_corp, bsns_year=test_year, db=db)
    print(f"-> 수집된 항목 수: {len(res1)}개")

    print("\n[2차 호출] 동일 조건 재요청 (DB 캐시 Hit 검증)")
    res2 = dart_service.fetch_financial_data(corp_code=test_corp, bsns_year=test_year, db=db)
    print(f"-> 캐시 조회된 항목 수: {len(res2)}개")

    db.close()

def test_agent_execution_pipeline():
    print("\n==================================================")
    print(" 2. LangGraph Agent 및 Tool Binding 동작 테스트")
    print("==================================================")

    # 에이전트 질문 전송 (정형/비정형 융합 질의)
    query = "삼성전자(00126380)의 2023년 재무 데이터를 바탕으로 클라우드 전환 제안서 요약을 작성해줘."
    print(f"사용자 요청: {query}\n")

    inputs = {"messages": [HumanMessage(content=query)]}

    try:
        # 1. LangSmith 실행 추적 컨텍스트 (선택한 프로젝트명으로 웹 UI 자동 전송)
        with tracing_v2_enabled(project_name="b2b-sales-gpt") as cb:
            
            # 2. 콘솔에서 실행 단계(노드 및 도구 호출)를 실시간으로 출력
            print("[실행 프로세스 스트리밍]")
            print("--------------------------------------------------")
            
            config = {} # 콜백 없이 clean하게 실행
            
            # graph.stream()을 활용하면 노드별 진행 상황을 실시간으로 터미널에 찍을 수 있습니다.
            for event in sales_agent.stream(inputs, config=config):
                for node_name, state in event.items():
                    print(f"\n [Node 완료]: {node_name}")
                    last_msg = state["messages"][-1]
                    
                    # Tool 호출 요청 메시지인 경우 (LLM이 Tool을 쓰겠다고 판단한 시점)
                    if getattr(last_msg, "tool_calls", None):
                        for tool_call in last_msg.tool_calls:
                            print(f" [Tool 호출 요청]: {tool_call['name']}(인자: {tool_call['args']})")
                    
                    # Tool 실행 결과 메시지인 경우
                    elif last_msg.type == "tool":
                        print(f" [Tool 실행 완료]: {last_msg.name}")

            # 3. 전체 실행 결과 수집
            final_state = sales_agent.invoke(inputs, config=config)

            print("\n[에이전트 최종 응답]")
            print("--------------------------------------------------")
            print(final_state["messages"][-1].content)
            print("--------------------------------------------------")
            
            # 4. LangSmith 웹 UI 대시보드 바로가기 URL 출력
            if cb and cb.latest_run:
                print(f"\n [LangSmith Trace URL]: https://smith.langchain.com/o/.../r/{cb.latest_run.id}")

            print("-> Agent 동작 성공!")

    except Exception as e:
        print(f"-> Agent 실행 failure: {str(e)}")


# def test_agent_execution_pipeline():
#     print("\n==================================================")
#     print(" 2. LangGraph Agent 및 Tool Binding 동작 테스트")
#     print("==================================================")

#     # 에이전트 질문 전송 (정형/비정형 융합 질의)
#     query = "삼성전자(00126380)의 2023년 재무 데이터를 바탕으로 클라우드 전환 제안서 요약을 작성해줘."
#     print(f"사용자 요청: {query}\n")

#     inputs = {"messages": [HumanMessage(content=query)]}
    
#     try:
#         # 에이전트 실행 및 추론 과정 출력
#         final_state = sales_agent.invoke(inputs)
        
#         print("\n[에이전트 최종 응답]")
#         print("--------------------------------------------------")
#         print(final_state["messages"][-1].content)
#         print("--------------------------------------------------")
#         print("-> Agent 동작 성공!")
        
#     except Exception as e:
#         print(f"-> Agent 실행 failure: {str(e)}")


if __name__ == "__main__":
    # 1. DB 캐싱 테스트
    test_dart_caching_pipeline()
    
    # 2. 에이전트 동작 테스트
    test_agent_execution_pipeline()