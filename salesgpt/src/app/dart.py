# dart.py
# DART Open API 수집 및 데이터 정제 모듈
# 기업의 주요 재무제표 데이터를 비동기로 수집, schemas.py로 검증한 뒤 model.py를 이용해 SQLite DB에 저장을 완료

import logging
import httpx
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.config import settings
from app.models import Company, FinancialReport
from app.schemas import CompanyCreate, FinancialReportCreate  # 기업 생성 요청 DTO, 재무제표 요청 생성 DTO

# 로깅 설정
logger = logging.getLogger(__name__)

# API 전용 호출 도메인
DART_BASE_URL = 'https://opendart.fss.or.kr/api'

# 실제 httpx 요청 시 결합되는 URL
url = f"{DART_BASE_URL}/fnlttSinglAcnt.json" 
# -> https://opendart.fss.or.kr/api/fnlttSinglAcnt.json

class DartService:
    """DART Open API 수집 및 DB 저장 비지니스 로직"""

    def __init__(self, db: Session):
        self.db = db
        self.api_key = settings.DART_API_KEY

    async def fetch_financial_data(self, corp_code: str, bsns_year: str, reprt_code: str = '11011') -> Optional[List[Dict[str, Any]]]:
       """
       DART Open API(단일회사 주요계정 API)를 비동기 호출하여 원본 데이터를 수신합니다.
       - reprt_code: 11011(사업보고서), 11012(반기), 11013(1분기), 11014(3분기)
       """ 

       url = f'{DART_BASE_URL}/fnlttSinglAcnt.json'   
       params = {
           'crtfc_key': self.api_key,
           'corp_code': corp_code,
           'bsns_year': bsns_year,
           'reprt_code': reprt_code
       }

       # 비동기 컨텍스트 매니저 : 리소스의 비동기적 할당과 해제를 관리함
       async with httpx.AsyncClient(timeout=10.0) as client:
           try:
               response = await client.get(url, params=params)
               response.raise_for_status()
               data = response.json()
           except httpx.HTTPError as e:
               logger.error(f'DART API 통신 오류 (corp_code: {corp_code}): {e}')    
               return None

       # DART 응답 상채 코드 확인(000: 정상)    
       status = data.get('status')
       if status != '000':
           message = data.get('message', 'Unkown error')
           logger.warning(f'DART API 응답 오류 [코드: {status}]: {message}')
           return None
       
       return data.get('list', [])

    def save_company_if_not_exists(self, corp_code: str, corp_name: str, stock_code: Optional[str] = None) -> Company:
        """
        Company 정보를 DB에 등록합니다. 이미 존재할 경우 해당 객체를 반환합니다.
        """
        try:
            company = self.db.query(Company).filter(Company.corp_code == corp_code).first()
            if not company:
                company_dto = CompanyCreate(
                    corp_code=corp_code,
                    corp_name=corp_name,
                    stock_code=stock_code
                )
                company = Company(**company_dto.model_dump())
                self.db.add(company)
                self.db.commit()
                self.db.refresh(company)
                logger.info(f'신규 기업 등록 완료: {corp_name} ({corp_code})')
            return company
        
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"기업 정보 저장 중 DB 오류 발생 (corp_code: {corp_code}): {e}")
            return None
        
        except Exception as e:
            self.db.rollback()
            logger.error(f"기업 정보 저장 중 예기치 못한 오류 발생: {e}")
            return None    
        
    # 
    async def syn_company_finacials(self, corp_code: str, bsns_year: str) -> bool:
        """
        DART 데이터를 수집하여 Company 및 FinancialReport를 DB에 수집/갱신 합니다.
        """
        raw_items = await self.fetch_financial_data(corp_code=corp_code, bsns_year=bsns_year) # DART Open API 호출, 원본 데이터 수집
        if not raw_items:
            logger.warning(f'수집된 재무 데이터가 없습니다. (corp_code: {corp_code}, year: {bsns_year})')
            return False

        # 1. 기업 정보 기본 등록/확인
        first_item = raw_items[0]
        corp_name = first_item.get('coap_name', '미상')
        stock_code = first_item.get('stock_code')

        self.save_company_if_not_exists(corp_code=corp_code, corp_name=corp_name, stock_code=stock_code) # 테이블 DB 등록

        # 2. 재무제표 계정 항목 데이터 정제 및 DB 저장
        saved_count = 0
        for item in raw_items:
            account_nm = item.get('account_nm')
            if not account_nm:
                continue

            # Pydantic DTO를 통한 데이터 정제(쉼표 제거, 정수 변환 등)
            report_dto = FinancialReportCreate(
                corp_code=corp_code,
                bsns_year=bsns_year,
                reprt_code=item.get('reprt_code', '11011'),
                account_nm=account_nm,
                thstrm_amount=item.get('thstrm_amount=')
            )

            # 중복 체크(동일 기업, 동일 연도, 동일 계정명)
            existing_report = self.db.query(FinancialReport).filter(
                FinancialReport.corp_code == corp_code,
                FinancialReport.bsns_year == bsns_year,
                FinancialReport.account_nm == account_nm
            ).first()

            if existing_report:
                # 기존 데이터 갱신
                existing_report.thstrm_amount = report_dto.thstrm_amount
            else:
                # 신규 데이터 추가
                report_obj = FinancialReport(**report_dto.model_dump())
                self.db.add(report_obj)
            saved_count += 1    

        self.db.commit()
        logger.info(f'재무 데이터 수집 완료: {corp_name} {bsns_year}년도 계정 {saved_count}건 저장/갱신' )

# 외부 단일 호출용 비동기 도우미 함수
async def fetch_and_save_company_financials(corp_code: str, bsns_year: str, db: Session):
    service = DartService(db=db)
    return await service.syn_company_finacials(corp_code=corp_code, bsns_year=bsns_year)

        





        
                              
    

              
