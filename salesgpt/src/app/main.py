# app/main.py
"""
SalesGPT B2B 제안서 생성 엔진의 FastAPI 메인 엔드포인트 모듈.
LangGraph 에이전트를 RESTful API 형태로 노출합니다.
"""

from typing import List, Optional
from fastapi import FastAPI, HTTPException, status
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field

from app.agent import sales_agent


# 1. FastAPI 앱 인스턴스 생성
app = FastAPI(
    title='SalesGPR B2B Proposal Engin API',
    description='DART 재무 정보 및 LlamaIndex Vector RAG 지식 베이스를 활용한 B2B 영업 제안서 자동 생성 에이전트 API',
    version='1.0.0',
)

# 2. Request / Response Pydantic 스키마 정의
class ProposalRequest(BaseModel):
    prompt: str =Field(
        ...,
        description='B2B 제안서 작성 관련 요청 사항',
        examples='삼성전자 2023년 재무 상태 분석하고 클라우드 전환 사업 제안서 개요 작성해줘.'
    )
    thread_id: Optional[str] = Field(
        default='default_session',
        description='세션 관리를 위한 쓰레드 ID (추후 대화 맥락 유지용)'
    )

class ProposalResponse(BaseModel):
    status: str = Field('success', description='응답 상태')    
    result: str = Field('...', description='SalesGPT 에이전트가 최종 생성한 제안서/답변 내용')

# 3. Health Check 엔드 포인트
@app.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    """서버 정상 작동 여부 확인용 엔드 포인트"""
    return {'status': 'healthy', 'service': 'SalesGPT API'}

# 4. SalesGPT 실행 엔드포인트
@app.post(
    "/api/v1/generate-proposal",
    response_model=ProposalResponse,
    status_code=status.HTTP_200_OK,
    summary="B2B 제안서 문맥 생성 요청",
)
def generate_proposal(request: ProposalRequest):
    """사용자의 요청을 LangGraph State Machine으로 전달하여 DART 데이터 및 RAG 지식을 융합한 답변을 반환합니다."""

    if not request.prompt.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='요청 프롬프트가 비어 있습니다.'
        )
    try:
        # LangGraph 입력 스키마 구성
        inputs = {'messages': [HumanMessage(content=request.prompt)]}

        # LangGraph 에이전트 실행(마지막 노드 결과 반환)
        final_state = sales_agent.invoke(inputs)

        # 최종 반환 메시지 추출
        last_message = final_state['messages'][-1]
        final_result = last_message.content

        return ProposalResponse(
            status='success',
            result=final_result
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'SalesGPT 처리 중 오류 발생: {str(e)}'
        )    