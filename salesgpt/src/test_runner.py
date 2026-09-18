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
        # 에이전트 실행 및 추론 과정 출력
        final_state = sales_agent.invoke(inputs)
        
        print("\n[에이전트 최종 응답]")
        print("--------------------------------------------------")
        print(final_state["messages"][-1].content)
        print("--------------------------------------------------")
        print("-> Agent 동작 성공!")
        
    except Exception as e:
        print(f"-> Agent 실행 failure: {str(e)}")


if __name__ == "__main__":
    # 1. DB 캐싱 테스트
    test_dart_caching_pipeline()
    
    # 2. 에이전트 동작 테스트
    test_agent_execution_pipeline()