# app/mcp_tools.py
"""
LangGraph Agent가 사용할 도구(Tools)를 정의하는 모듈.
비즈니스 로직(Service Layer)과 API 의존성을 분리하여 @tool 데코레이터로 래핑합니다.
"""

from typing import Optional
from langchain_core.tools import tool

from app.dart import get_dart_service
from app.vector import get_vector_service


@tool
def search_company_financials(corp_code: str, bsns_year: str, reprt_code: str = "11011") -> str:
    """DART API를 통해 특정 기업의 재무제표(재무상태표, 손익계산서 등) 데이터를 조회합니다.

    Args:
        corp_code (str): 고유번호 8자리 (예: '00126380')
        bsns_year (str): 사업연도 4자리 (예: '2023')
        reprt_code (str): 보고서 코드 (11011: 사업보고서, 11012: 반기, 11013: 1분기, 11014: 3분기). 기본값 '11011'

    Returns:
        str: 재무 데이터 조회 결과 요약 또는 에러 메시지
    """
    try:
        dart_service = get_dart_service()
        financial_data = dart_service.get_financial_statement(
            corp_code=corp_code,
            bsns_year=bsns_year,
            reprt_code=reprt_code
        )
        
        if not financial_data:
            return f"기업코드 {corp_code}의 {bsns_year}년도 재무 데이터를 찾을 수 없습니다."
            
        # Agent가 읽기 쉽도록 주요 지표 가공 및 텍스트 렌더링
        lines = [f"=== 기업 {corp_code} ({bsns_year}년 보고서) 재무 정보 ==="]
        for item in financial_data:
            account_nm = item.get("account_nm", "항목명 없음")
            thstrm_amount = item.get("thstrm_amount", "0")
            lines.append(f"- {account_nm}: {thstrm_amount}원")
            
        return "\n".join(lines)

    except Exception as e:
        return f"DART 재무 데이터 조회 중 오류가 발생했습니다: {str(e)}"


@tool
def query_proposal_knowledge_base(query: str, similarity_top_k: int = 3) -> str:
    """LlamaIndex기반 Vector DB(Chroma)에서 B2B 제안서 작성에 필요한 유사 지식 및 템플릿 문맥을 검색합니다.

    Args:
        query (str): 검색할 질의어 (예: 'cloud 인프라 구축 제안서 보안 요건')
        similarity_top_k (int): 반환할 상위 문서 조각(Chunk) 개수. 기본값 3

    Returns:
        str: 검색된 B2B 문맥 정보 목록
    """
    try:
        vector_service = get_vector_service()
        results = vector_service.query_knowledge_base(
            query=query, 
            similarity_top_k=similarity_top_k
        )
        
        if not results:
            return f"질의어 '{query}'에 대한 관련 제안서 지식을 찾지 못했습니다."
            
        formatted_context = [f"=== B2B 제안서 지식 베이스 검색 결과 ('{query}') ==="]
        for idx, text in enumerate(results, start=1):
            formatted_context.append(f"[{idx}] {text.strip()}\n")
            
        return "\n".join(formatted_context)

    except Exception as e:
        return f"지식 베이스(RAG) 검색 중 오류가 발생했습니다: {str(e)}"


# Agent 노드 생성을 위한 도구 목록 바인딩 Export
ALL_SALES_TOOLS = [
    search_company_financials,
    query_proposal_knowledge_base,
]