# dart.py
# DART Open API 수집 및 데이터 정제 모듈
# 기업의 주요 재무제표 데이터를 비동기로 수집, schemas.py로 검증한 뒤 model.py를 이용해 SQLite DB에 저장을 완료

import logging
import requests
from typing import List, Optional
from sqlalchemy.orm import Session

from config import settings, SessionLocal
from models import FinancialReport
from schemas import DartApiResponseSchema

logger = logging.getLogger(__name__)

DART_BASE_URL = "https://opendart.fss.or.kr/api"

class DartService:
    def __init__(self, api_key: Optional[str] = None, db: Optional[Session] = None):
        self.db = db
        self.api_key = api_key or settings.DART_API_KEY
        self.base_url = DART_BASE_URL

    def fetch_financial_data(
        self, 
        corp_code: str, 
        bsns_year: str, 
        reprt_code: str = '11011',
        db: Optional[Session] = None
    ) -> List[dict]:
        """
        1. DB 캐시 확인 (Hit 시 즉시 반환)
        2. 캐시 없으면 DART Open API 호출
        3. Pydantic 스키마 검증 후 SQLite DB 저장 및 반환
        """
        # db 세션 주입 여부 확인 및 자체 세션 관리
        own_session = False
        active_db = db or self.db
        if active_db is None:
            active_db = SessionLocal()
            own_session = True

        try:
            # --------------------------------------------------
            # Step 1: SQLite DB 캐시 조회
            # --------------------------------------------------
            cached_reports = active_db.query(FinancialReport).filter(
                FinancialReport.corp_code == corp_code,
                FinancialReport.bsns_year == bsns_year,
                FinancialReport.reprt_code == reprt_code
            ).all()

            if cached_reports:
                logger.info(f"[CACHE HIT] DB에서 {corp_code} ({bsns_year}년) 데이터를 읽어왔습니다.")
                return [
                    {
                        "account_nm": item.account_nm,
                        "thstrm_amount": item.thstrm_amount,
                        "sj_div": item.sj_div
                    }
                    for item in cached_reports
                ]

            # --------------------------------------------------
            # Step 2: DB에 없을 경우 Open DART API 호출
            # --------------------------------------------------
            logger.info(f"[API CALL] DART Open API를 통해 {corp_code} ({bsns_year}년) 데이터를 수집합니다.")
            url = f"{self.base_url}/fnlttSinglAcntAll.json"
            # url = f"{self.base_url}/fnlttSinglAcnt.json"

            params = {
                'crtfc_key': self.api_key,
                'corp_code': corp_code,
                'bsns_year': bsns_year,
                'reprt_code': reprt_code
            }

            response = requests.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            raw_json = response.json()

            print('dart.py raw_json ==>', raw_json)

            # --------------------------------------------------
            # Step 3: Pydantic DTO 기반 응답 데이터 검증
            # --------------------------------------------------
            parsed_data = DartApiResponseSchema(**raw_json)

            print('dart.py parsed_data ==>', parsed_data)

            if parsed_data.status != '000' or not parsed_data.list:
                logger.warning(f"DART API 응답 메세지 [코드: {parsed_data.status}]: {parsed_data.message}")
                return []

            # --------------------------------------------------
            # Step 4: DB 저장 (ORM 캐싱) 및 반환 데이터 구성
            # --------------------------------------------------
            new_records = []
            result_list = []

            for item in parsed_data.list:
                report_entity = FinancialReport(
                    corp_code=corp_code,
                    bsns_year=bsns_year,
                    reprt_code=reprt_code,
                    sj_div=item.sj_div,
                    account_nm=item.account_nm,
                    thstrm_amount=item.thstrm_amount or "0"
                )
                new_records.append(report_entity)

                result_list.append({
                    "account_nm": item.account_nm,
                    "thstrm_amount": item.thstrm_amount or "0",
                    "sj_div": item.sj_div
                })

            active_db.bulk_save_objects(new_records)
            active_db.commit()
            logger.info(f"[CACHE SAVE] {len(new_records)}건의 데이터를 SQLite DB에 캐싱했습니다.")

            print('dart.py result_list ==>', result_list)

            return result_list

        except Exception as e:
            active_db.rollback()
            logger.error(f"DART 수집 및 캐싱 처리 실패 (corp_code: {corp_code}): {e}")
            return []

        finally:
            if own_session:
                active_db.close()


# 싱글톤 팩토리 패턴
_dart_service_instance: Optional[DartService] = None

def get_dart_service() -> DartService:
    global _dart_service_instance
    if _dart_service_instance is None:
        _dart_service_instance = DartService()
    return _dart_service_instance


        





        
                              
    

              
