# app/schemas.py
# Pydantic v2 DTO (DART 수신 데이터 파싱 및 수치 정제)
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field, field_validator

# ==========================================
# Company Schemas
# ==========================================

class CompanyBase(BaseModel):
    corp_code: str = Field(..., min_length=8, max_length=8, description="고유 기업 고유번호 (8자리)")
    corp_name: str = Field(..., max_length=100, description="기업명")
    stock_code: Optional[str] = Field(None, max_length=6, description="상장 주식 코드 (6자리)")
    modify_date: Optional[str] = Field(None, max_length=8, description="최종 수정일자 (YYYYMMDD)")


class CompanyCreate(CompanyBase):
    """기업 생성 요청 DTO"""
    pass


class CompanyResponse(CompanyBase):
    """기업 정보 응답 DTO"""
    model_config = ConfigDict(from_attributes=True)


# ==========================================
# FinancialReport Schemas
# ==========================================

class FinancialReportBase(BaseModel):
    corp_code: str = Field(..., min_length=8, max_length=8, description="기업 고유번호")
    bsns_year: str = Field(..., min_length=4, max_length=4, description="사업 연도 (YYYY)")
    reprt_code: str = Field(..., min_length=5, max_length=5, description="보고서 코드 (11011: 사업보고서)")
    sj_div: Optional[str] = Field(None, max_length=10, description="재무제표 구분 (BS, IS, CIS 등)")
    account_nm: str = Field(..., max_length=100, description="재무 계정명 (예: 매출액, 영업이익)")
    thstrm_amount: Optional[int] = Field(0, description="당기 금액 (원)")

    @field_validator('thstrm_amount', mode='before')
    @classmethod
    def parse_thstrm_amount(cls, value):
        """
        DART API 수신 데이터 중 콤마(,)가 포함된 문자열이나 빈 값을 정수로 변환합니다.
        """
        if isinstance(value, str):
            clean_val = value.replace(',', '').strip()
            if not clean_val or clean_val == '-':
                return 0
            return int(clean_val)
        if value is None:
            return 0
        return value


class FinancialReportCreate(FinancialReportBase):
    """재무제표 생성 요청 DTO"""
    pass


class FinancialReportResponse(FinancialReportBase):
    """재무제표 응답 DTO"""
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# Combined & API Payload Schemas
# ==========================================

class CompanyWithFinancialsResponse(CompanyResponse):
    """기업 정보 및 재무제표 목록 통합 응답 DTO"""
    financial_reports: List[FinancialReportResponse] = []

    model_config = ConfigDict(from_attributes=True)


class DartFetchRequest(BaseModel):
    """DART API 수집 요청 DTO"""
    corp_code: str = Field(..., min_length=8, max_length=8, description="수집 대상 기업 고유번호")
    bsns_year: str = Field(..., min_length=4, max_length=4, description="수집 대상 연도 (YYYY)")


# ==========================================
# Open DART Raw API Response Parsing Schemas
# ==========================================

class DartApiResponseItem(BaseModel):
    """DART API 원본 단일 항목 파싱 스키마"""
    rcept_no: Optional[str] = None
    bsns_year: Optional[str] = None
    corp_code: Optional[str] = None
    stock_code: Optional[str] = None
    reprt_code: Optional[str] = None
    account_nm: str = Field(..., description="계정명")
    sj_div: Optional[str] = Field(None, description="재무제표 구분")
    thstrm_nm: Optional[str] = None
    thstrm_amount: Optional[str] = Field(None, description="당기금액 (문자열)")
    frmtrm_nm: Optional[str] = None
    frmtrm_amount: Optional[str] = None
    ord: Optional[str] = None


class DartApiResponseSchema(BaseModel):
    """DART Open API 원본 응답 최상위 구조 스키마"""
    status: str = Field(..., description="응답 상태 코드 (000: 정상)")
    message: str = Field(..., description="응답 메시지")
    list: Optional[List[DartApiResponseItem]] = Field(default=[], description="재무제표 계정 목록")