"""ImportantList.md에 정의한 OpenDART API의 비동기 호출 클라이언트.

MCP 도구나 FastAPI 핸들러에서 ``await``로 호출할 수 있도록 모든 네트워크
함수를 비동기로 제공한다. JSON 응답은 딕셔너리로, corpCode·공시 원문·XBRL
파일 응답은 ZIP/XML 바이너리로 반환한다.
"""

from __future__ import annotations

import os
import asyncio
import re
import time
import zipfile
from datetime import date
from decimal import Decimal, InvalidOperation
from io import BytesIO
from typing import Any, Mapping

import httpx

from corp_code_sync import find_corp_codes_by_name



from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent
DEBUG_LOG = Path(SRC_DIR) / "mcp_debug.log"

def debug_log(*args):
    with DEBUG_LOG.open("a", encoding="utf-8") as f:
        print(*args, file=f, flush=True)


# OpenDART API 요청 주소를 만들 때 사용하는 공통 기본 URL이다.
OPEN_DART_BASE_URL = "https://opendart.fss.or.kr/api"
# 상장·비상장 법인의 고유번호가 담긴 ZIP/XML 파일을 받는 엔드포인트다.
CORP_CODE_ENDPOINT = "corpCode.xml"
# 법인의 기본 개황 정보를 조회하는 엔드포인트다.
COMPANY_ENDPOINT = "company.json"
# 공시 목록과 접수번호를 검색하는 엔드포인트다.
DISCLOSURE_LIST_ENDPOINT = "list.json"
# 특정 법인의 주요 재무 계정을 조회하는 엔드포인트다.
SINGLE_ACCOUNT_ENDPOINT = "fnlttSinglAcnt.json"
# 특정 법인의 주요 재무지표를 조회하는 엔드포인트다.
SINGLE_INDEX_ENDPOINT = "fnlttSinglIndx.json"
# 특정 법인의 전체 재무제표 계정을 조회하는 엔드포인트다.
SINGLE_ACCOUNT_ALL_ENDPOINT = "fnlttSinglAcntAll.json"
# 공시 원문 ZIP/XML 파일을 받는 기본 엔드포인트다.
DOCUMENT_ENDPOINT = "document.xml"
# 공시 원문 JSON 응답을 시도할 때 사용하는 보조 엔드포인트다.
DOCUMENT_JSON_ENDPOINT = "document.json"
# 여러 법인의 주요 재무 계정을 비교 조회하는 엔드포인트다.
MULTI_ACCOUNT_ENDPOINT = "fnlttMultiAcnt.json"
# 여러 법인의 재무지표를 비교 조회하는 엔드포인트다.
MULTI_INDEX_ENDPOINT = "fnlttCmpnyIndx.json"
# XBRL 재무제표의 계정 분류 체계를 조회하는 엔드포인트다.
XBRL_TAXONOMY_ENDPOINT = "xbrlTaxonomy.json"
# XBRL 원본 재무제표 ZIP/XML 파일을 받는 엔드포인트다.
XBRL_FILE_ENDPOINT = "fnlttXbrl.xml"

# 정기보고서(사업·반기·분기) 종류를 구분하는 OpenDART 보고서 코드 집합이다.
REPORT_CODES = {"11013", "11012", "11014", "11011"}
# 개별재무제표(OFS)와 연결재무제표(CFS)를 허용하는 재무제표 구분 코드 집합이다.
FS_DIVISIONS = {"OFS", "CFS"}


class OpenDartApiError(RuntimeError):
    """OpenDART가 HTTP 또는 API 오류를 반환했을 때 발생하는 예외."""

    def __init__(self, status: str | None, message: str | None):
        self.status = status
        self.message = message or "OpenDART API 오류"
        super().__init__(f"OpenDART 오류 {status}: {self.message}")


def get_api_key(api_key: str | None = None) -> str:
    """OpenDART 인증키를 인자로 받거나 환경변수에서 반환한다.

    Args:
        api_key: 호출자가 직접 전달할 40자리 OpenDART 인증키. 생략하면
            ``DART_API_KEY``와 ``OPENDART_API_KEY``를 순서대로 확인한다.

    Returns:
        사용할 인증키 문자열.

    Raises:
        RuntimeError: 인증키를 찾지 못한 경우.
    """

    key = api_key or os.getenv("DART_API_KEY") or os.getenv("OPENDART_API_KEY")
    if not key:
        raise RuntimeError(
            "DART_API_KEY 또는 OPENDART_API_KEY 환경변수가 설정되어 있지 않습니다."
        )
    return key


def _require_corp_code(corp_code: str) -> str:
    """기업 고유번호가 숫자 8자리인지 검증하고 반환한다."""

    if len(corp_code) != 8 or not corp_code.isdigit():
        raise ValueError("corp_code는 숫자 8자리여야 합니다.")
    return corp_code


def _require_report_params(
    corp_code: str,
    bsns_year: str,
    reprt_code: str,
) -> dict[str, str]:
    """재무 API 공통 필수 파라미터를 검증하고 딕셔너리로 반환한다.

    Args:
        corp_code: OpenDART 기업 고유번호 8자리.
        bsns_year: 사업연도 4자리 문자열(예: ``"2024"``).
        reprt_code: 보고서 코드. 1분기 ``11013``, 반기 ``11012``,
            3분기 ``11014``, 사업보고서 ``11011``.

    Returns:
        검증된 ``corp_code``, ``bsns_year``, ``reprt_code`` 딕셔너리.
    """

    _require_corp_code(corp_code)
    if len(bsns_year) != 4 or not bsns_year.isdigit():
        raise ValueError("bsns_year는 숫자 4자리여야 합니다.")
    if reprt_code not in REPORT_CODES:
        raise ValueError(f"reprt_code는 {sorted(REPORT_CODES)} 중 하나여야 합니다.")
    return {
        "corp_code": corp_code,
        "bsns_year": bsns_year,
        "reprt_code": reprt_code,
    }


def _report_code_from_name(report_name: str) -> str | None:
    """공시 보고서명에서 OpenDART 재무 API용 보고서 코드를 추정한다."""

    if "사업보고서" in report_name:
        return "11011"
    if "반기보고서" in report_name:
        return "11012"
    if "3분기보고서" in report_name or "분기보고서" in report_name:
        return "11014" if "3분기" in report_name else "11013"
    return None


def _business_year_from_report(report: Mapping[str, Any]) -> str:
    """공시 보고서명 또는 접수일에서 재무 API 사업연도를 얻는다."""

    report_name = str(report.get("report_nm") or "")
    year_match = re.search(r"20\d{2}", report_name)
    if year_match:
        return year_match.group(0)
    receipt_date = str(report.get("rcept_dt") or "")
    if len(receipt_date) >= 4 and receipt_date[:4].isdigit():
        # 보고서명에 기간이 없을 때만 접수연도를 보정값으로 사용한다.
        return str(int(receipt_date[:4]) - 1)
    raise ValueError(
        "공시 결과에서 사업연도를 확인할 수 없습니다. bsns_year를 직접 지정하세요."
    )


def _normalize_numeric_text(value: Any) -> dict[str, Any]:
    """금액·지표 문자열을 검증하고 결측 상태를 보존한다.

    Args:
        value: 쉼표가 포함된 금액 문자열, 지표 문자열, ``None`` 또는 ``-``.

    Returns:
        원본 문자열(``raw``), 정규화 문자열(``value``), 사용 가능 여부
        (``available``)를 담은 딕셔너리. 결측값은 0으로 바꾸지 않는다.
    """

    if value is None:
        return {"raw": None, "value": None, "available": False}
    raw = str(value).strip()
    if not raw or raw in {"-", "—"}:
        return {"raw": raw or None, "value": None, "available": False}
    normalized = raw.replace(",", "")
    try:
        Decimal(normalized)
    except (InvalidOperation, ValueError):
        return {"raw": raw, "value": None, "available": False}
    return {"raw": raw, "value": normalized, "available": True}


def _report_source_metadata(
    report: Mapping[str, Any],
    fs_div: str | None = None,
    stlm_dt: str | None = None,
) -> dict[str, Any]:
    """재무 수치의 출처를 재현할 수 있는 공통 메타데이터를 만든다."""

    return {
        "corp_code": report.get("corp_code"),
        "corp_name": report.get("corp_name"),
        "bsns_year": report.get("bsns_year"),
        "reprt_code": report.get("reprt_code"),
        "report_nm": report.get("report_nm"),
        "rcept_no": report.get("rcept_no"),
        "rcept_dt": report.get("rcept_dt"),
        "fs_div": fs_div,
        "stlm_dt": stlm_dt,
    }



# OpenDART 보고서 코드의 기간 의미를 명시적으로 관리한다.
REPORT_PERIOD_TYPES = {
    "11013": "Q1",
    "11012": "H1",
    "11014": "Q3",
    "11011": "ANNUAL",
}

# 재무상태표는 특정 시점 값이고, 손익·현금흐름은 해당 보고기간 누적값으로 관리한다.
INSTANT_STATEMENT_TYPES = {"BS", "SCE"}
FLOW_STATEMENT_TYPES = {"IS", "CIS", "CF"}

# AI/리포트 계층에서 사용할 표준 계정 ID. account_nm은 회사별 표시 차이를 고려해
# 아래 alias를 통해 보수적으로 매핑하며, 매핑되지 않은 계정은 원본 ID를 그대로 보존한다.
CANONICAL_ACCOUNT_ALIASES: dict[str, tuple[str, ...]] = {
    "TOTAL_ASSETS": (
        "자산총계",
        "총자산",
    ),
    "CURRENT_ASSETS": (
        "유동자산",
    ),
    "NONCURRENT_ASSETS": (
        "비유동자산",
    ),
    "CASH_AND_EQUIVALENTS": (
        "현금및현금성자산",
        "현금 및 현금성자산",
    ),

    "TOTAL_LIABILITIES": (
        "부채총계",
        "총부채",
    ),
    "CURRENT_LIABILITIES": (
        "유동부채",
    ),
    "NONCURRENT_LIABILITIES": (
        "비유동부채",
    ),

    "TOTAL_EQUITY": (
        "자본총계",
        "총자본",
    ),
    "EQUITY_ATTRIBUTABLE_TO_OWNERS": (
        "지배기업의 소유주에게 귀속되는 자본",
        "지배기업 소유주지분",
        "지배기업의 소유주지분",
    ),
    "NONCONTROLLING_INTERESTS": (
        "비지배지분",
    ),
    "PAID_IN_CAPITAL": (
        "자본금",
    ),
    "CAPITAL_SURPLUS": (
        "자본잉여금",
    ),
    "RETAINED_EARNINGS": (
        "이익잉여금",
    ),
    "ACCUMULATED_OTHER_COMPREHENSIVE_INCOME": (
        "기타포괄손익누계액",
    ),
    "OTHER_EQUITY": (
        "기타자본",
    ),

    "REVENUE": (
        "매출액",
        "수익(매출액)",
        "영업수익",
    ),
    "COST_OF_SALES": (
        "매출원가",
    ),
    "GROSS_PROFIT": (
        "매출총이익",
    ),
    "OPERATING_PROFIT": (
        "영업이익",
    ),
    "PROFIT_BEFORE_TAX": (
        "법인세비용차감전순이익",
        "세전이익",
    ),
    "INCOME_TAX_EXPENSE": (
        "법인세비용",
    ),
    "NET_INCOME": (
        "당기순이익",
        "반기순이익",
        "분기순이익",
    ),
    "NET_INCOME_ATTRIBUTABLE_TO_OWNERS": (
        "지배기업의 소유주에게 귀속되는 당기순이익",
        "지배기업의 소유주에게 귀속되는 순이익",
    ),

    "TOTAL_COMPREHENSIVE_INCOME": (
        "총포괄손익",
        "총포괄이익",
    ),
    "TOTAL_COMPREHENSIVE_INCOME_ATTRIBUTABLE_TO_OWNERS": (
        "지배기업의 소유주에게 귀속되는 총포괄손익",
    ),

    "OPERATING_CASH_FLOW": (
        "영업활동현금흐름",
    ),
    "INVESTING_CASH_FLOW": (
        "투자활동현금흐름",
    ),
    "FINANCING_CASH_FLOW": (
        "재무활동현금흐름",
    ),
}


def _clean_account_name(value: Any) -> str:
    """계정명 비교용 공백/특수공백을 정리한다."""
    return re.sub(r"\s+", "", str(value or "")).replace("·", "")


def _clean_account_detail(value: Any) -> str:
    """SCE account_detail의 표시 차이를 비교 가능하게 정규화한다.

    회사/보고서마다 달라질 수 있는 XBRL 표시용 문구만 제거하고,
    계정의 경제적 의미를 임의로 보정하지 않는다.
    """
    text = _clean_account_name(value)
    for token in ("[구성요소]", "[member]", "[Member]", "[MEMBER]"):
        text = text.replace(token, "")
    return text


def _period_metadata(report: Mapping[str, Any], statement_type: str | None, stlm_dt: str | None) -> dict[str, Any]:
    """보고서 코드와 재무제표 구분으로 기간 의미를 명시한다."""
    reprt_code = str(report.get("reprt_code") or "")
    period_type = REPORT_PERIOD_TYPES.get(reprt_code, "UNKNOWN")
    end_date = stlm_dt or None
    if statement_type in INSTANT_STATEMENT_TYPES:
        semantic_type = "INSTANT"
    elif statement_type in FLOW_STATEMENT_TYPES:
        semantic_type = "ANNUAL" if period_type == "ANNUAL" else "CUMULATIVE"
    else:
        semantic_type = period_type

    year = str(report.get("bsns_year") or "")
    suffix = {
        "11013": "Q1",
        "11012": "H1",
        "11014": "Q3",
        "11011": "FY",
    }.get(reprt_code)
    period_key = f"{year}{suffix}" if year and suffix else None
    period_start = f"{year}-01-01" if semantic_type in {"CUMULATIVE", "ANNUAL"} and len(year) == 4 else None
    return {
        "report_period_type": period_type,
        "period_type": semantic_type,
        "period_key": period_key,
        "period_start": period_start,
        "period_end": end_date,
        "period_basis": (
            "BALANCE_SHEET_AS_OF" if semantic_type == "INSTANT"
            else "FULL_YEAR" if semantic_type == "ANNUAL"
            else "YTD_CUMULATIVE" if semantic_type == "CUMULATIVE"
            else "UNKNOWN"
        ),
    }


# OpenDART 지표명에서 단위를 보수적으로 판별하기 위한 명시적 규칙이다.
# 숫자 자체(idx_val)만으로 단위를 추정하지 않고, 지표명이 명확한 경우에만 적용한다.
INDEX_PERCENT_EXACT_NAMES = {
    "순이익률", "총포괄이익률", "매출총이익률", "매출원가율", "판관비율",
    "총자산영업이익률", "자기자본비율", "부채비율", "유동비율",
    "유동부채비율", "비유동부채비율", "비유동비율", "금융비용부담률",
    "배당성향", "재무레버리지", "ROE", "ROA",
}

INDEX_COUNT_EXACT_NAMES = {
    "총자산회전율", "재고자산회전율", "자기자본회전율", "타인자본회전율",
}

INDEX_MULTIPLE_EXACT_NAMES = {
    "이자보상배율",
}

INDEX_PERCENT_SUFFIXES = ("증가율", "성장률")


def _normalize_index_name(value: Any) -> str:
    """지표명 비교용 공백/특수공백을 제거한다."""
    return re.sub(r"\s+", "", str(value or ""))


def _infer_index_unit(index_name: Any) -> dict[str, Any]:
    """지표명만으로 안전하게 확인 가능한 단위를 판별한다.

    단위가 명확한 지표는 ``KNOWN``으로 표시한다. 반대로 재무레버리지처럼
    기관/데이터셋별 표현이 달라질 수 있는 항목은 숫자를 보고 임의로 %/배를
    선택하지 않고 ``UNKNOWN``으로 남긴다.
    """
    name = _normalize_index_name(index_name)

    if name in INDEX_PERCENT_EXACT_NAMES:
        return {
            "unit": "%",
            "unit_status": "KNOWN",
            "unit_source": "INDEX_NAME_EXACT",
            "unit_confidence": "HIGH",
        }

    if any(name.endswith(suffix) for suffix in INDEX_PERCENT_SUFFIXES):
        return {
            "unit": "%",
            "unit_status": "KNOWN",
            "unit_source": "INDEX_NAME_SUFFIX",
            "unit_confidence": "HIGH",
        }

    if name in INDEX_COUNT_EXACT_NAMES:
        return {
            "unit": "회",
            "unit_status": "KNOWN",
            "unit_source": "INDEX_NAME_EXACT",
            "unit_confidence": "HIGH",
        }

    if name in INDEX_MULTIPLE_EXACT_NAMES:
        return {
            "unit": "배",
            "unit_status": "KNOWN",
            "unit_source": "INDEX_NAME_EXACT",
            "unit_confidence": "HIGH",
        }

    # '매출원가/재고자산'처럼 비율 계산을 나타내지만 표시단위를 확정할 수
    # 없는 지표는 숫자를 보고 임의로 '배' 또는 '회'로 바꾸지 않는다.
    return {
        "unit": None,
        "unit_status": "UNKNOWN",
        "unit_source": "UNKNOWN",
        "unit_confidence": "NONE",
    }


def _index_interpretation_metadata(
    index_name: Any,
    unit_info: Mapping[str, Any],
) -> dict[str, Any]:
    """OpenDART 원천지표의 표시 가능성과 해석 가능성을 분리한다.

    핵심 원칙:
    - 원천값 존재 여부(source_value_status)와 단위 확인 여부(unit_status)는 별개다.
    - 단위가 확인되어도 산식/연환산 여부가 확인되지 않으면 경제적 해석을 허용하지 않는다.
    - 이 함수는 원천지표를 계산지표로 가장하지 않는다.
    """
    unit = unit_info.get("unit")
    unit_status = unit_info.get("unit_status")

    if unit_status == "KNOWN":
        interpretation_reason = (
            "원천값과 표시 단위는 확인되지만 산식 및 연환산 여부를 확인하지 않아 "
            "경제적 의미 해석을 보류합니다."
        )
    else:
        interpretation_reason = (
            "원천값은 존재하지만 표시 단위를 지표명만으로 확정할 수 없고 "
            "산식 및 연환산 여부도 확인하지 않아 해석을 보류합니다."
        )

    return {
        # OpenDART가 제공한 값이라는 사실은 확인 가능하지만, 정의가 확인됐다는 뜻은 아니다.
        "source_value_status": "SOURCE_PROVIDED",
        "definition_status": "UNVERIFIED",
        "formula_status": "UNVERIFIED",
        "formula_source": None,
        "formula": None,
        "annualized": None,
        "annualization_status": "UNVERIFIED",
        "interpretation_allowed": False,
        "interpretation_reason": interpretation_reason,
        "period_semantics_status": "REPORT_PERIOD_ONLY",
        "calculation_status": "NOT_CALCULATED",
    }


def validate_normalized_indices(
    indices: dict[str, list[dict[str, Any]]] | None,
) -> dict[str, Any]:
    """정규화된 OpenDART 지표의 해석 가능 상태를 검증한다.

    숫자 자체가 존재한다고 해서 산식이나 연환산 여부까지 확인된 것으로 간주하지 않는다.
    따라서 지표 정의가 확인되지 않은 항목은 ``WARNING``으로 남기고 원천값은 보존한다.
    """
    warnings: list[dict[str, Any]] = []
    checked = 0

    for category, rows in (indices or {}).items():
        for row in rows:
            if not row.get("available"):
                continue
            checked += 1
            if not row.get("interpretation_allowed", False):
                warnings.append({
                    "category": category,
                    "idx_code": row.get("idx_code"),
                    "idx_nm": row.get("idx_nm"),
                    "reason": row.get("interpretation_reason"),
                    "unit": row.get("unit"),
                    "unit_status": row.get("unit_status"),
                    "source_value_status": row.get("source_value_status"),
                    "calculation_status": row.get("calculation_status"),
                    "formula_status": row.get("formula_status"),
                    "annualized": row.get("annualized"),
                    "annualization_status": row.get("annualization_status"),
                })

    return {
        "status": "WARNING" if warnings else "PASS",
        "warnings": warnings,
        "checked_indices": checked,
    }


def _canonical_metric_id(
    account_name: Any,
    *,
    account_detail: Any = None,
    sj_div: str = "",
    account_id: Any = None,
) -> str | None:
    """OpenDART 계정을 canonical metric으로 보수적으로 매핑한다.

    원칙:
    1. 의미가 명확한 IFRS account_id를 최우선으로 사용한다.
    2. 재무제표 종류(BS/IS/CIS/CF/SCE)를 반드시 고려한다.
    3. SCE의 account_detail은 실제 자본 잔액 행(ifrs-full_Equity)에서만 사용한다.
    4. SCE movement를 자본 잔액 metric으로 오인하지 않는다.
    5. 확실하지 않은 계정은 None으로 남긴다.
    """
    cleaned = _clean_account_name(account_name)
    detail = _clean_account_detail(account_detail)
    statement = str(sj_div or "").strip().upper()
    xbrl_id = str(account_id or "").strip()

    explicit_ifrs_map = {
        "ifrs-full_ProfitLossAttributableToOwnersOfParent":
            "NET_INCOME_ATTRIBUTABLE_TO_OWNERS",
        "ifrs-full_ComprehensiveIncomeAttributableToOwnersOfParent":
            "TOTAL_COMPREHENSIVE_INCOME_ATTRIBUTABLE_TO_OWNERS",
    }
    explicit_metric = explicit_ifrs_map.get(xbrl_id)
    if explicit_metric is not None:
        return explicit_metric

    # SCE: account_detail은 '열/구성요소' 의미일 수 있으므로
    # 실제 Equity 잔액 행에서만 구성요소 판정에 사용한다.
    if statement == "SCE":
        if xbrl_id != "ifrs-full_Equity":
            return None

        if "비지배지분" in detail:
            return "NONCONTROLLING_INTERESTS"
        if "기타포괄손익누계액" in detail:
            return "ACCUMULATED_OTHER_COMPREHENSIVE_INCOME"
        if "이익잉여금" in detail:
            return "RETAINED_EARNINGS"
        if "자본잉여금" in detail:
            return "CAPITAL_SURPLUS"
        if "기타자본" in detail:
            return "OTHER_EQUITY"
        if "자본금" in detail:
            return "PAID_IN_CAPITAL"
        if any(token in detail for token in (
            "지배기업소유주귀속분",
            "지배기업의소유주귀속분",
            "지배기업소유주지분",
            "지배기업의소유주지분",
        )):
            return "EQUITY_ATTRIBUTABLE_TO_OWNERS"

        # 최상위 자본총계만 TOTAL_EQUITY로 인정한다.
        # 세부 구성요소인지 확실하지 않은 행은 None으로 남겨 가짜 conflict를 막는다.
        is_total_name = cleaned in {
            _clean_account_name("자본총계"),
            _clean_account_name("총자본"),
        }
        looks_like_component = (
            "|" in detail
            or "구성요소" in detail
            or "소유주" in detail
            or "비지배" in detail
        )
        if is_total_name and not looks_like_component:
            return "TOTAL_EQUITY"
        return None

    statement_metric_ids = {
        "BS": {
            "TOTAL_ASSETS", "CURRENT_ASSETS", "NONCURRENT_ASSETS",
            "CASH_AND_EQUIVALENTS", "TOTAL_LIABILITIES",
            "CURRENT_LIABILITIES", "NONCURRENT_LIABILITIES",
            "TOTAL_EQUITY", "EQUITY_ATTRIBUTABLE_TO_OWNERS",
            "NONCONTROLLING_INTERESTS", "PAID_IN_CAPITAL",
            "CAPITAL_SURPLUS", "RETAINED_EARNINGS",
            "ACCUMULATED_OTHER_COMPREHENSIVE_INCOME", "OTHER_EQUITY",
        },
        "IS": {
            "REVENUE", "COST_OF_SALES", "GROSS_PROFIT",
            "OPERATING_PROFIT", "PROFIT_BEFORE_TAX",
            "INCOME_TAX_EXPENSE", "NET_INCOME",
            "NET_INCOME_ATTRIBUTABLE_TO_OWNERS",
            "TOTAL_COMPREHENSIVE_INCOME",
            "TOTAL_COMPREHENSIVE_INCOME_ATTRIBUTABLE_TO_OWNERS",
        },
        "CIS": {
            "REVENUE", "COST_OF_SALES", "GROSS_PROFIT",
            "OPERATING_PROFIT", "PROFIT_BEFORE_TAX",
            "INCOME_TAX_EXPENSE", "NET_INCOME",
            "NET_INCOME_ATTRIBUTABLE_TO_OWNERS",
            "TOTAL_COMPREHENSIVE_INCOME",
            "TOTAL_COMPREHENSIVE_INCOME_ATTRIBUTABLE_TO_OWNERS",
        },
        "CF": {
            "OPERATING_CASH_FLOW", "INVESTING_CASH_FLOW",
            "FINANCING_CASH_FLOW",
        },
    }

    allowed_metrics = statement_metric_ids.get(statement)
    if allowed_metrics is None:
        return None

    for metric_id in allowed_metrics:
        aliases = CANONICAL_ACCOUNT_ALIASES.get(metric_id, ())
        if any(cleaned == _clean_account_name(alias) for alias in aliases):
            return metric_id

    return None

def _decimal(value: Any) -> Decimal | None:
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None


def _almost_equal(a: Decimal, b: Decimal, tolerance: Decimal = Decimal("1")) -> bool:
    return abs(a - b) <= tolerance


def validate_normalized_accounts(accounts: list[dict[str, Any]]) -> dict[str, Any]:
    """정규화된 재무제표의 기본 산술 관계를 검증한다.

    회사별 표시 구조 차이를 고려해 존재하는 계정만 검증하며, 검증 불가능한 관계는
    오류로 취급하지 않는다. tolerance는 OpenDART 금액 단위의 반올림 오차를 고려한다.
    """
    warnings: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    by_metric: dict[str, list[dict[str, Any]]] = {}

    for row in accounts:
        metric_id = row.get("canonical_metric_id")
        if metric_id and row.get("amount_available") and row.get("amount") is not None:
            by_metric.setdefault(metric_id, []).append(row)

    def one(metric_id: str, *, statement_type: str | None = None) -> dict[str, Any] | None:
        rows = by_metric.get(metric_id, [])
        if statement_type is not None:
            rows = [row for row in rows if row.get("sj_div") == statement_type]
        if not rows:
            return None
        unique_values = {str(row.get("amount")) for row in rows if row.get("amount") is not None}
        if len(unique_values) != 1:
            return None
        return rows[0]

    def value(metric_id: str, *, statement_type: str | None = None) -> Decimal | None:
        row = one(metric_id, statement_type=statement_type)
        return _decimal(row.get("amount")) if row else None

    assets = value("TOTAL_ASSETS", statement_type="BS")
    liabilities = value("TOTAL_LIABILITIES", statement_type="BS")
    equity = value("TOTAL_EQUITY", statement_type="BS")
    if assets is not None and liabilities is not None and equity is not None:
        if not _almost_equal(assets, liabilities + equity):
            errors.append({"check": "assets_equals_liabilities_plus_equity", "actual": str(assets), "expected": str(liabilities + equity)})

    current_assets = value("CURRENT_ASSETS", statement_type="BS")
    noncurrent_assets = value("NONCURRENT_ASSETS", statement_type="BS")
    if assets is not None and current_assets is not None and noncurrent_assets is not None:
        if not _almost_equal(assets, current_assets + noncurrent_assets):
            errors.append({"check": "assets_breakdown", "actual": str(assets), "expected": str(current_assets + noncurrent_assets)})

    current_liabilities = value("CURRENT_LIABILITIES", statement_type="BS")
    noncurrent_liabilities = value("NONCURRENT_LIABILITIES", statement_type="BS")
    if liabilities is not None and current_liabilities is not None and noncurrent_liabilities is not None:
        if not _almost_equal(liabilities, current_liabilities + noncurrent_liabilities):
            errors.append({"check": "liabilities_breakdown", "actual": str(liabilities), "expected": str(current_liabilities + noncurrent_liabilities)})

    revenue = value("REVENUE", statement_type="IS") or value("REVENUE", statement_type="CIS")
    cogs = value("COST_OF_SALES", statement_type="IS") or value("COST_OF_SALES", statement_type="CIS")
    gross = value("GROSS_PROFIT", statement_type="IS") or value("GROSS_PROFIT", statement_type="CIS")
    if revenue is not None and cogs is not None and gross is not None:
        if not _almost_equal(gross, revenue - cogs):
            warnings.append({"check": "gross_profit_reconciliation", "actual": str(gross), "expected": str(revenue - cogs), "reason": "원천 재무제표의 매출총이익과 매출액-매출원가 계산값이 일치하지 않습니다."})

    owners_equity = value("EQUITY_ATTRIBUTABLE_TO_OWNERS", statement_type="SCE")
    nci = value("NONCONTROLLING_INTERESTS", statement_type="SCE")
    sce_total_equity = value("TOTAL_EQUITY", statement_type="SCE")
    if owners_equity is not None and nci is not None and sce_total_equity is not None:
        if not _almost_equal(sce_total_equity, owners_equity + nci):
            warnings.append({"check": "equity_attributable_plus_nci", "actual": str(sce_total_equity), "expected": str(owners_equity + nci), "reason": "SCE 자본총계와 지배기업 소유주 귀속분 + 비지배지분이 일치하지 않습니다."})

    return {
        "status": "ERROR" if errors else ("WARNING" if warnings else "PASS"),
        "errors": errors,
        "warnings": warnings,
        "checked_accounts": len(accounts),
    }


def detect_metric_conflicts(accounts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """동일한 재무 문맥의 동일 canonical metric에서 서로 다른 원천값을 탐지한다."""
    buckets: dict[tuple[Any, ...], list[dict[str, Any]]] = {}
    for row in accounts:
        metric_id = row.get("canonical_metric_id")
        if not metric_id or not row.get("amount_available") or row.get("amount") is None:
            continue
        source = row.get("source") or {}
        key = (
            metric_id,
            row.get("fs_div") or source.get("fs_div"),
            row.get("sj_div"),
            row.get("period_key"),
            row.get("period_type"),
            row.get("period_start"),
            row.get("period_end"),
        )
        buckets.setdefault(key, []).append(row)

    conflicts: list[dict[str, Any]] = []
    for key, rows in buckets.items():
        values = {str(r.get("amount")) for r in rows if r.get("amount") is not None}
        if len(values) <= 1:
            continue
        conflicts.append({
            "status": "CONFLICT",
            "metric_id": key[0],
            "fs_div": key[1],
            "sj_div": key[2],
            "period_key": key[3],
            "period_type": key[4],
            "period_start": key[5],
            "period_end": key[6],
            "values": sorted(values),
            "candidates": [
                {
                    "account_nm": r.get("account_nm"),
                    "account_detail": r.get("account_detail"),
                    "amount": r.get("amount"),
                    "amount_raw": r.get("amount_raw"),
                    "account_id": r.get("account_id"),
                    "sj_div": r.get("sj_div"),
                    "amount_field": r.get("amount_field"),
                    "amount_semantics": r.get("amount_semantics"),
                    "source": r.get("source"),
                }
                for r in rows
            ],
        })
    return conflicts

def build_compact_financial_dto(
    company: Mapping[str, Any],
    report: Mapping[str, Any],
    canonical_metrics: list[dict[str, Any]],
    validation: Mapping[str, Any],
    conflicts: list[dict[str, Any]],
) -> dict[str, Any]:
    """LLM에 전달할 최소 재무 DTO를 만든다. RAW 응답은 포함하지 않는다."""
    safe_metrics = []
    conflict_keys = {
        (c.get("metric_id"), c.get("sj_div"), c.get("period_key"))
        for c in conflicts
    }
    for m in canonical_metrics:
        if (m.get("metric_id"), m.get("statement_type"), m.get("period_key")) in conflict_keys:
            continue
        safe_metrics.append({
            k: m.get(k)
            for k in (
                "metric_id", "metric_name", "value", "unit", "statement_type",
                "fs_div", "period_type", "period_key", "period_start",
                "period_end", "source", "validation_status", "validated",
            )
            if m.get(k) is not None
        })
    return {
        "company": {
            "corp_code": company.get("corp_code"),
            "corp_name": company.get("corp_name") or company.get("corp_name_eng"),
        },
        "report": {
            "rcept_no": report.get("rcept_no"),
            "rcept_dt": report.get("rcept_dt"),
            "report_nm": report.get("report_nm"),
            "bsns_year": report.get("bsns_year"),
            "reprt_code": report.get("reprt_code"),
            "fs_div": report.get("fs_div"),
            "period_key": f"{report.get('bsns_year')}{ {'11012':'H1','11013':'Q1','11014':'Q3','11011':'FY'}.get(str(report.get('reprt_code')), '') }".rstrip(),
        },
        "metrics": safe_metrics,
        "validation": {
            "status": "CONFLICT" if conflicts else validation.get("status"),
            "errors": validation.get("errors", []),
            "warnings": validation.get("warnings", []),
            "conflicts": conflicts,
        },
    }


def build_canonical_metrics(accounts: list[dict[str, Any]], indices: dict[str, list[dict[str, Any]]] | None = None) -> list[dict[str, Any]]:
    """AI/보고서 계층에서 사용할 검증 가능한 표준 metric 목록을 만든다."""
    metrics: list[dict[str, Any]] = []
    seen: set[tuple[str, str | None, str | None, str | None]] = set()

    for row in accounts:
        metric_id = row.get("canonical_metric_id")
        if not metric_id or not row.get("amount_available"):
            continue
        source = row.get("source") or {}
        key = (metric_id, row.get("sj_div"), row.get("period_key"), row.get("amount"))
        if key in seen:
            continue
        seen.add(key)
        metrics.append({
            "metric_id": metric_id,
            "metric_name": row.get("account_nm"),
            "account_detail": row.get("account_detail"),
            "account_id": row.get("account_id"),
            "value": row.get("amount"),
            "value_raw": row.get("amount_raw"),
            "unit": row.get("currency") or "KRW",
            "statement_type": row.get("sj_div"),
            "fs_div": row.get("fs_div"),
            "period_type": row.get("period_type"),
            "period_key": row.get("period_key"),
            "period_start": row.get("period_start"),
            "period_end": row.get("period_end"),
            "source": source,
            "validated": True,
            "validation_status": "PENDING_RECONCILIATION",
            "formula": None,
        })

    for category, rows in (indices or {}).items():
        for row in rows:
            if not row.get("available"):
                continue
            metrics.append({
                "metric_id": f"DART_INDEX:{row.get('idx_code') or row.get('idx_nm')}",
                "metric_name": row.get("idx_nm"),
                "value": row.get("value"),
                "value_raw": row.get("value_raw"),
                "unit": row.get("unit"),
                "unit_status": row.get("unit_status"),
                "unit_source": row.get("unit_source"),
                "unit_confidence": row.get("unit_confidence"),
                "scale": row.get("scale", 1),
                "statement_type": None,
                "fs_div": (row.get("source") or {}).get("fs_div"),
                "period_type": row.get("period_type"),
                "report_period_type": row.get("report_period_type"),
                "period_semantics": row.get("period_semantics"),
                "period_key": row.get("period_key"),
                "period_start": row.get("period_start"),
                "period_end": row.get("period_end"),
                "source": row.get("source"),
                "validated": True,
                "validation_status": (
                    "SOURCE_OFFICIAL_DART_INDEX_UNINTERPRETED"
                    if not row.get("interpretation_allowed")
                    else "SOURCE_OFFICIAL_DART_INDEX_INTERPRETATION_ALLOWED"
                ),
                "source_value_status": row.get("source_value_status", "SOURCE_PROVIDED"),
                "calculation_status": row.get("calculation_status", "NOT_CALCULATED"),
                "definition_status": row.get("definition_status"),
                "formula_status": row.get("formula_status"),
                "formula_source": row.get("formula_source"),
                "formula": row.get("formula"),
                "annualized": row.get("annualized"),
                "annualization_status": row.get("annualization_status", "UNVERIFIED"),
                "interpretation_allowed": row.get("interpretation_allowed", False),
                "interpretation_reason": row.get("interpretation_reason"),
                "index_category": category,
                "idx_code": row.get("idx_code"),
            })
    return metrics

def normalize_account_item(
    item: Mapping[str, Any],
    report: Mapping[str, Any],
) -> dict[str, Any]:
    """전체 재무제표 계정을 의미·기간 메타데이터와 함께 정규화한다.

    누적 필드가 필요한 손익계산서 계열에서 누적값이 없으면 다른 필드로 조용히
    대체하지 않는다. 금융 리포트에서는 기간 의미가 바뀌는 fallback이 더 위험하기 때문이다.
    """
    sj_div = str(item.get("sj_div") or "")
    reprt_code = str(report.get("reprt_code") or item.get("reprt_code") or "")

    if sj_div in FLOW_STATEMENT_TYPES:
        amount_field = "thstrm_amount" if reprt_code == "11011" else "thstrm_add_amount"
    elif sj_div in INSTANT_STATEMENT_TYPES:
        amount_field = "thstrm_amount"
    else:
        # 미지의 재무제표 구분은 가장 보수적으로 현재기 금액만 선택하고 경고를 남긴다.
        amount_field = "thstrm_amount"

    amount = _normalize_numeric_text(item.get(amount_field))
    warnings: list[str] = []
    if not amount["available"] and sj_div in FLOW_STATEMENT_TYPES and reprt_code != "11011":
        warnings.append(f"필수 누적 필드 {amount_field}가 비어 있습니다. thstrm_amount로 fallback하지 않았습니다.")
    if sj_div not in FLOW_STATEMENT_TYPES | INSTANT_STATEMENT_TYPES:
        warnings.append(f"알 수 없는 sj_div={sj_div!r}; thstrm_amount를 선택했습니다.")

    period = _period_metadata(report, sj_div, item.get("thstrm_dt"))
    source = _report_source_metadata(
        report,
        fs_div=item.get("fs_div"),
        stlm_dt=item.get("thstrm_dt"),
    )

    canonical_metric_id = _canonical_metric_id(
        item.get("account_nm"),
        account_detail=item.get("account_detail"),
        sj_div=sj_div,
        account_id=item.get("account_id"),
    )

    if sj_div == "SCE":
        sce_balance_metrics = {
            "TOTAL_EQUITY",
            "EQUITY_ATTRIBUTABLE_TO_OWNERS",
            "NONCONTROLLING_INTERESTS",
            "PAID_IN_CAPITAL",
            "CAPITAL_SURPLUS",
            "RETAINED_EARNINGS",
            "ACCUMULATED_OTHER_COMPREHENSIVE_INCOME",
            "OTHER_EQUITY",
        }
        amount_semantics = (
            "INSTANT_BALANCE"
            if canonical_metric_id in sce_balance_metrics
            else "SCE_MOVEMENT_OR_UNCLASSIFIED"
        )
    elif sj_div in FLOW_STATEMENT_TYPES:
        amount_semantics = "ANNUAL_FLOW" if reprt_code == "11011" else "CUMULATIVE_FLOW"
    elif sj_div in INSTANT_STATEMENT_TYPES:
        amount_semantics = "INSTANT_BALANCE"
    else:
        amount_semantics = "UNKNOWN"

    return {
        "account_id": item.get("account_id"),
        "account_nm": item.get("account_nm"),
        "account_detail": item.get("account_detail"),
        "sj_div": sj_div,
        "fs_div": item.get("fs_div"),
        "amount": amount["value"],
        "amount_raw": amount["raw"],
        "amount_available": amount["available"],
        "amount_field": amount_field,
        "amount_semantics": amount_semantics,
        "currency": item.get("currency"),
        "period_type": period["period_type"],
        "report_period_type": period["report_period_type"],
        "period_key": period["period_key"],
        "period_start": period["period_start"],
        "period_end": period["period_end"],
        "period_basis": period["period_basis"],
        "canonical_metric_id": canonical_metric_id,
        "validation_warnings": warnings,
        "source": source,
    }


def normalize_index_item(
    item: Mapping[str, Any],
    report: Mapping[str, Any],
) -> dict[str, Any]:
    """OpenDART 공식 재무지표를 값·단위·기간·산식 상태와 함께 정규화한다.

    원칙:
    1. ``idx_val`` 원천값은 절대 재계산하거나 임의 변환하지 않는다.
    2. 지표명이 명확하면 단위를 별도 메타데이터로 판별한다.
    3. 단위가 확인되어도 산식/평균잔액/연환산 여부가 확인되지 않으면
       ``interpretation_allowed=False``를 유지한다.
    4. 원천값, 단위, 정의 상태를 각각 독립적으로 관리해 '단위 미확인'과
       '산식 미확인'을 구분한다.
    """
    value = _normalize_numeric_text(item.get("idx_val"))
    period = _period_metadata(report, None, item.get("stlm_dt"))
    source = _report_source_metadata(
        report,
        fs_div=item.get("fs_div"),
        stlm_dt=item.get("stlm_dt"),
    )

    unit_info = _infer_index_unit(item.get("idx_nm"))
    interpretation = _index_interpretation_metadata(
        item.get("idx_nm"),
        unit_info,
    )

    return {
        "idx_cl_code": item.get("idx_cl_code"),
        "idx_cl_nm": item.get("idx_cl_nm"),
        "idx_code": item.get("idx_code"),
        "idx_nm": item.get("idx_nm"),
        "value": value["value"],
        "value_raw": value["raw"],
        "available": value["available"],
        "source_value_status": (
            "SOURCE_PROVIDED" if value["available"] else "SOURCE_MISSING"
        ),
        "calculation_status": "NOT_CALCULATED",

        # 단위 메타데이터: 값과 별도로 보존한다.
        "unit": unit_info["unit"],
        "unit_status": unit_info["unit_status"],
        "unit_source": unit_info["unit_source"],
        "unit_confidence": unit_info["unit_confidence"],
        "scale": 1,

        # 기간: 지표 API 값의 기준 보고기간을 명시하되,
        # 이것만으로 연환산/분기화 등의 의미를 추론하지 않는다.
        "period_type": period["report_period_type"],
        "report_period_type": period["report_period_type"],
        "period_semantics": interpretation["period_semantics_status"],
        "period_key": period["period_key"],
        "period_start": period["period_start"],
        "period_end": period["period_end"],
        "stlm_dt": item.get("stlm_dt"),

        # 정의/산식/연환산 상태: 현재 클라이언트가 확인하지 못한 것은 명시적으로 보류한다.
        "source_value_status": interpretation["source_value_status"] if value["available"] else "SOURCE_MISSING",
        "calculation_status": interpretation["calculation_status"],
        "definition_status": interpretation["definition_status"],
        "formula_status": interpretation["formula_status"],
        "formula_source": interpretation["formula_source"],
        "formula": interpretation["formula"],
        "annualized": interpretation["annualized"],
        "annualization_status": interpretation["annualization_status"],
        "interpretation_allowed": interpretation["interpretation_allowed"] if value["available"] else False,
        "interpretation_reason": interpretation["interpretation_reason"],
        "source": source,
    }


def classify_canonical_metric_for_report(metric: Mapping[str, Any]) -> dict[str, Any]:
    """Canonical metric을 보고서 표시 등급으로 분류한다.

    등급은 우열을 의미하지 않는다. 원천재무제표 값과 원천지표 값의
    "검증/해석 가능 상태"를 구분하기 위한 기술적 상태값이다.

    Returns:
        ``SOURCE_FINANCIAL_STATEMENT``, ``SOURCE_INDEX_UNINTERPRETED``,
        ``SOURCE_INDEX_INTERPRETABLE`` 중 하나와 보고서용 설명.
    """
    if metric.get("statement_type"):
        return {
            "report_class": "SOURCE_FINANCIAL_STATEMENT",
            "report_label": "원천 재무제표 수치",
            "interpretation_allowed": True,
            "reason": "OpenDART 재무제표 계정의 원천값으로 기간·재무제표 구분을 함께 보존함",
        }

    if metric.get("interpretation_allowed"):
        return {
            "report_class": "SOURCE_INDEX_INTERPRETABLE",
            "report_label": "원천 재무지표",
            "interpretation_allowed": True,
            "reason": "원천지표의 정의·산식·기간 의미가 확인된 상태",
        }

    return {
        "report_class": "SOURCE_INDEX_UNINTERPRETED",
        "report_label": "원천 재무지표(해석 제한)",
        "interpretation_allowed": False,
        "reason": metric.get("interpretation_reason") or "지표 정의/산식/연환산 여부 미확인",
    }


def get_validated_canonical_metrics(report_data: Mapping[str, Any]) -> list[dict[str, Any]]:
    """검증 오류가 없는 보고서에서만 AI/PDF 입력용 canonical metric을 반환한다.

    ``canonical.metrics``에는 원천값을 보존하기 위해 오류가 있어도 metric이 남아 있을 수 있다.
    보고서 생성 계층에서는 이 함수를 사용해 validation ERROR가 발생한 보고서의 수치를 차단한다.
    WARNING은 허용하되 ``validation_status``를 함께 전달한다.
    """
    canonical = report_data.get("canonical") or {}
    validation = canonical.get("validation") or {}
    if validation.get("status") == "ERROR":
        return []
    return list(canonical.get("metrics") or [])


class OpenDartImportantClient:
    """ImportantList.md의 OpenDART API를 비동기로 호출하는 클라이언트.

    Args:
        api_key: OpenDART 인증키. 생략하면 환경변수에서 읽는다.
        timeout: 각 HTTP 요청의 기본 타임아웃(초).
        max_connections: 동시에 사용할 HTTP 연결 수.

    Returns:
        ``async with`` 블록에서 재사용 가능한 비동기 API 클라이언트.
    """

    def __init__(
        self,
        api_key: str | None = None,
        timeout: float = 30.0,
        max_connections: int = 20,
    ) -> None:
        self.api_key = get_api_key(api_key)
        self.timeout = timeout
        self.max_connections = max_connections
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "OpenDartImportantClient":
        """HTTP 연결 풀을 열고 클라이언트를 반환한다."""

        limits = httpx.Limits(
            max_connections=self.max_connections,
            max_keepalive_connections=min(self.max_connections, 10),
        )
        self._client = httpx.AsyncClient(
            base_url=OPEN_DART_BASE_URL,
            timeout=self.timeout,
            limits=limits,
        )
        return self

    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        """HTTP 연결 풀을 닫는다."""

        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def _request_json(
        self,
        endpoint: str,
        params: Mapping[str, str | int | None],
    ) -> dict[str, Any]:
        """JSON API를 호출하고 정상 응답 딕셔너리를 반환한다.

        Args:
            endpoint: ``company.json`` 같은 OpenDART API 파일명.
            params: 인증키를 제외한 API 요청 파라미터.

        Returns:
            OpenDART의 원본 JSON 응답 딕셔너리(``status``, ``message``, ``list`` 등).

        Raises:
            RuntimeError: ``async with`` 외부에서 호출한 경우.
            OpenDartApiError: HTTP 오류 또는 OpenDART ``status``가 ``000``이 아닌 경우.
        """

        if self._client is None:
            raise RuntimeError("클라이언트는 async with 블록 안에서 사용해야 합니다.")
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", endpoint.rsplit("/", 1)[-1]):
            raise ValueError("OpenDART API 엔드포인트 파일명만 지정할 수 있습니다.")
        request_params = {
            "crtfc_key": self.api_key,
            **{
                key: value
                for key, value in params.items()
                if value is not None and key != "crtfc_key"
            },
        }
        response = await self._client.get(endpoint, params=request_params)
        response.raise_for_status()
        payload = response.json()
        if payload.get("status") != "000":
            raise OpenDartApiError(payload.get("status"), payload.get("message"))
        return payload

    async def _request_binary(
        self,
        endpoint: str,
        params: Mapping[str, str | int | None],
    ) -> bytes:
        """ZIP/XML 파일 API를 호출하고 원본 바이트를 반환한다."""

        if self._client is None:
            raise RuntimeError("클라이언트는 async with 블록 안에서 사용해야 합니다.")
        request_params = {
            "crtfc_key": self.api_key,
            **{
                key: value
                for key, value in params.items()
                if value is not None and key != "crtfc_key"
            },
        }
        response = await self._client.get(endpoint, params=request_params)
        response.raise_for_status()
        content = response.content
        content_type = response.headers.get("content-type", "").lower()
        if "json" in content_type or not zipfile.is_zipfile(BytesIO(content)):
            try:
                payload = response.json()
            except ValueError:
                raise OpenDartApiError(None, response.text[:500]) from None
            raise OpenDartApiError(payload.get("status"), payload.get("message"))
        return content

    async def call_json_api(
        self,
        endpoint: str,
        params: Mapping[str, str | int | None] | None = None,
    ) -> dict[str, Any]:
        """ImportantList에 없는 OpenDART JSON API도 비동기로 호출한다.

        Args:
            endpoint: API 파일명 또는 ``/api`` 기준 상대 경로.
            params: API별 요청 인자. ``crtfc_key``는 자동으로 추가된다.

        Returns:
            정상 OpenDART JSON 응답 딕셔너리.
        """

        normalized_endpoint = endpoint.strip("/")
        if normalized_endpoint.startswith("api/"):
            normalized_endpoint = normalized_endpoint[4:]
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", normalized_endpoint):
            raise ValueError("OpenDART API 엔드포인트 파일명만 지정할 수 있습니다.")
        return await self._request_json(normalized_endpoint, params or {})

    async def get_corp_code_zip(self) -> bytes:
        """기업 고유번호 ZIP(``corpCode.xml``)을 반환한다.

        Returns:
            ``CORPCODE.xml``을 포함한 ZIP 바이너리. 파일 저장은 호출자 책임이다.
        """

        return await self._request_binary(CORP_CODE_ENDPOINT, {})

    async def resolve_company_name(
        self,
        company_name: str,
        database_url: str | None = None,
        limit: int = 10,
    ) -> dict[str, Any]:
        """회사명을 CorpCode DB에서 찾아 단일 기업 정보를 반환한다.

        Args:
            company_name: 사용자가 입력한 기업명.
            database_url: CorpCode MySQL의 선택적 SQLAlchemy URL.
            limit: 후보 검색 최대 개수.

        Returns:
            ``corp_code``, 기업명, 종목코드가 포함된 기업 정보 딕셔너리.

        Raises:
            LookupError: 일치하는 기업이 없거나 후보가 여러 개인 경우.
        """

        candidates = await find_corp_codes_by_name(
            company_name,
            database_url=database_url,
            limit=limit,
        )
        if not candidates:
            raise LookupError(f"기업명 '{company_name}'에 해당하는 기업을 찾지 못했습니다.")
        if len(candidates) > 1:
            names = ", ".join(
                f"{item['corp_name']}({item['corp_code']})" for item in candidates
            )
            raise LookupError(
                f"기업명이 여러 기업과 일치합니다: {names}. "
                "정확한 기업명을 입력하세요."
            )
        return candidates[0]

    async def get_company(self, corp_code: str) -> dict[str, Any]:
        """기업개황(``company.json``)을 조회한다.

        Args:
            corp_code: 기업 고유번호 8자리.

        Returns:
            기업명, 대표자, 주소, 업종, 결산월 등이 담긴 원본 JSON 딕셔너리.
        """

        return await self._request_json(
            COMPANY_ENDPOINT,
            {"corp_code": _require_corp_code(corp_code)},
        )

    async def get_periodic_reports(
        self,
        corp_code: str,
        history_count: int = 1,
        database_url: str | None = None,
    ) -> list[dict[str, Any]]:
        """기업의 최신 정기보고서부터 과거 보고서 목록을 반환한다.

        Args:
            corp_code: 기업 고유번호 8자리.
            history_count: 반환할 보고서 수. ``1``이면 최신 보고서만 반환한다.
            database_url: 이 함수에서는 호환성을 위해 받지만 사용하지 않는다.

        Returns:
            정정공시를 하나로 합친 정기보고서 목록. 각 항목에는
            ``rcept_no``, ``report_nm``, ``rcept_dt``, ``reprt_code``,
            ``bsns_year``가 포함된다.
        """

        del database_url  # 회사 식별은 resolve_company_name에서 수행한다.
        _require_corp_code(corp_code)
        if history_count < 1:
            raise ValueError("history_count는 1 이상이어야 합니다.")

        periodic: dict[tuple[str, str], dict[str, Any]] = {}
        page_no = 1
        # 최신 정기보고서가 첫 100건 밖에 있을 가능성을 줄이기 위해 페이지를 순회한다.
        # 과도한 API 호출을 피하기 위해 최대 10페이지(1,000건)까지만 확인한다.
        while page_no <= 10:
            response = await self.search_disclosures(
                corp_code=corp_code,
                bgn_de="20150101",
                end_de=date.today().strftime("%Y%m%d"),
                page_no=page_no,
                page_count=100,
            )
            for item in response.get("list", []):
                report_name = str(item.get("report_nm") or "")
                reprt_code = _report_code_from_name(report_name)
                if reprt_code is None:
                    continue
                report = {
                    **item,
                    "reprt_code": reprt_code,
                    "bsns_year": _business_year_from_report(item),
                }
                key = (report["bsns_year"], reprt_code)
                previous = periodic.get(key)
                # 같은 사업연도·보고서의 정정본 중 가장 최근 접수본만 유지한다.
                if previous is None or (
                    str(report.get("rcept_no") or "")
                    > str(previous.get("rcept_no") or "")
                ):
                    periodic[key] = report
            page_no += 1
            if len(response.get("list", [])) < 100:
                break

        reports = sorted(
            periodic.values(),
            key=lambda item: (
                str(item.get("rcept_dt") or ""),
                str(item.get("rcept_no") or ""),
            ),
            reverse=True,
        )
        return reports[:history_count]

    async def get_company_financial_data(
        self,
        company_name: str,
        history_count: int = 1,
        fs_div: str = "CFS",
        database_url: str | None = None,
        include_raw: bool = False,
    ) -> dict[str, Any]:
        """회사명으로 최신 재무보고서와 선택한 과거 보고서를 수집한다.

        기존 조회/정규화/검증 로직은 변경하지 않고, 각 단계의 실행시간만
        ``mcp_debug.log``에 ``[PERF]`` 형식으로 기록한다.
        """

        total_started = time.perf_counter()

        async def perf_await(label: str, awaitable):
            started = time.perf_counter()
            try:
                return await awaitable
            finally:
                debug_log(f"[PERF] {label}: {time.perf_counter() - started:.3f}s")

        def perf_sync(label: str, func):
            started = time.perf_counter()
            try:
                return func()
            finally:
                debug_log(f"[PERF] {label}: {time.perf_counter() - started:.3f}s")

        try:
            if fs_div not in FS_DIVISIONS:
                raise ValueError("fs_div는 'OFS' 또는 'CFS'여야 합니다.")

            company = await perf_await(
                "resolve_company_name",
                self.resolve_company_name(company_name, database_url=database_url),
            )
            corp_code = company["corp_code"]

            reports = await perf_await(
                "get_periodic_reports",
                self.get_periodic_reports(corp_code, history_count),
            )

            async def collect(report: dict[str, Any]) -> dict[str, Any]:
                """한 보고서에 대한 기존 재무 API 호출과 후처리 시간을 측정한다."""

                report_started = time.perf_counter()
                report_code = report["reprt_code"]
                year = report["bsns_year"]
                report_label = f"{year}/{report_code}"

                async def timed_index(idx_cl_code: str, category: str):
                    return await perf_await(
                        f"{report_label} get_single_indices[{category}:{idx_cl_code}]",
                        self.get_single_indices(
                            corp_code, year, report_code, idx_cl_code
                        ),
                    )

                try:
                    accounts, indices, accounts_all = await asyncio.gather(
                        perf_await(
                            f"{report_label} get_single_accounts",
                            self.get_single_accounts(corp_code, year, report_code),
                        ),
                        asyncio.gather(
                            timed_index("M210000", "profitability"),
                            timed_index("M220000", "stability"),
                            timed_index("M230000", "growth"),
                            timed_index("M240000", "activity"),
                        ),
                        perf_await(
                            f"{report_label} get_single_accounts_all[{fs_div}]",
                            self.get_single_accounts_all(
                                corp_code, year, report_code, fs_div
                            ),
                        ),
                    )

                    index_payloads = {
                        category: payload
                        for category, payload in zip(
                            ("profitability", "stability", "growth", "activity"),
                            indices,
                        )
                    }

                    normalized_accounts = perf_sync(
                        f"{report_label} normalize_accounts",
                        lambda: [
                            normalize_account_item(row, report)
                            for row in accounts_all.get("list", [])
                        ],
                    )

                    normalized_indices = perf_sync(
                        f"{report_label} normalize_indices",
                        lambda: {
                            category: [
                                normalize_index_item(row, report)
                                for row in payload.get("list", [])
                            ]
                            for category, payload in index_payloads.items()
                        },
                    )

                    debug_log("=" * 100)
                    debug_log("NORMALIZED EQUITY ACCOUNTS")
                    for row in normalized_accounts:
                        text = str(row)
                        if any(keyword in text.upper() for keyword in [
                            "TOTAL_EQUITY",
                            "EQUITY_ATTRIBUTABLE_TO_OWNERS",
                            "NONCONTROLLING_INTERESTS",
                        ]):
                            debug_log(row)
                    debug_log("=" * 100)

                    account_validation = perf_sync(
                        f"{report_label} validate_normalized_accounts",
                        lambda: validate_normalized_accounts(normalized_accounts),
                    )
                    index_validation = perf_sync(
                        f"{report_label} validate_normalized_indices",
                        lambda: validate_normalized_indices(normalized_indices),
                    )
                    conflicts = perf_sync(
                        f"{report_label} detect_metric_conflicts",
                        lambda: detect_metric_conflicts(normalized_accounts),
                    )

                    debug_log("DETECTED CONFLICTS")
                    for conflict in conflicts:
                        debug_log(conflict)

                    canonical_metrics = perf_sync(
                        f"{report_label} build_canonical_metrics",
                        lambda: build_canonical_metrics(
                            normalized_accounts, normalized_indices
                        ),
                    )

                    validation_warnings = list(account_validation.get("warnings", []))
                    validation_warnings.extend(
                        {"type": "CONFLICT", **c} for c in conflicts
                    )
                    validation_warnings.extend(index_validation.get("warnings", []))
                    validation_errors = list(account_validation.get("errors", []))
                    validation = {
                        "status": "CONFLICT" if conflicts else (
                            "ERROR" if validation_errors else (
                                "WARNING" if validation_warnings else "PASS"
                            )
                        ),
                        "errors": validation_errors,
                        "warnings": validation_warnings,
                        "account_validation": account_validation,
                        "index_validation": index_validation,
                    }

                    conflicted_metric_keys = {
                        (c.get("metric_id"), c.get("sj_div"), c.get("period_key"))
                        for c in conflicts
                    }
                    for metric in canonical_metrics:
                        if str(metric.get("metric_id") or "").startswith("DART_INDEX:"):
                            continue
                        metric_key = (
                            metric.get("metric_id"),
                            metric.get("statement_type"),
                            metric.get("period_key"),
                        )
                        if metric_key in conflicted_metric_keys:
                            metric["validation_status"] = "CONFLICT"
                            metric["validated"] = False
                        else:
                            metric["validation_status"] = "PASS"
                            metric["validated"] = True

                    compact = perf_sync(
                        f"{report_label} build_compact_financial_dto",
                        lambda: build_compact_financial_dto(
                            company, report, canonical_metrics, validation, conflicts
                        ),
                    )

                    result = {
                        "report": report,
                        "canonical": {
                            "metrics": canonical_metrics,
                            "validation": validation,
                            "validated": validation["status"] not in {"ERROR", "CONFLICT"},
                        },
                        "compact": compact,
                        "source": _report_source_metadata(report, fs_div=fs_div),
                    }
                    if include_raw:
                        result["raw"] = {
                            "single_accounts": accounts,
                            "single_indices": index_payloads,
                            "single_accounts_all": accounts_all,
                        }
                    return result
                finally:
                    debug_log(
                        f"[PERF] {report_label} collect_total: "
                        f"{time.perf_counter() - report_started:.3f}s"
                    )

            report_data = await perf_await(
                "collect_reports_total",
                asyncio.gather(*(collect(report) for report in reports)),
            )

            company_detail = await perf_await(
                "get_company",
                self.get_company(corp_code),
            )

            return {
                "company": company,
                "company_detail": company_detail,
                "reports": list(report_data),
            }
        finally:
            debug_log(
                f"[PERF] get_company_financial_data TOTAL: "
                f"{time.perf_counter() - total_started:.3f}s"
            )

    async def search_disclosures(
        self,
        corp_code: str | None = None,
        bgn_de: str | None = None,
        end_de: str | None = None,
        last_reprt_at: str | None = None,
        pblntf_ty: str | None = None,
        pblntf_detail_ty: str | None = None,
        corp_cls: str | None = None,
        sort: str | None = None,
        sort_mth: str | None = None,
        page_no: int = 1,
        page_count: int = 100,
    ) -> dict[str, Any]:
        """공시검색(``list.json``) 결과를 조회한다.

        Args:
            corp_code: 선택적 기업 고유번호 8자리.
            bgn_de/end_de: 접수일 검색 구간(``YYYYMMDD``).
            last_reprt_at: 최종보고서만 조회할 때 ``"Y"`` 또는 ``"N"``.
            pblntf_ty/pblntf_detail_ty: 공시유형·상세유형 코드.
            corp_cls: 법인구분(``Y``, ``K``, ``N``, ``E``).
            sort/sort_mth: 정렬 기준과 정렬 방식.
            page_no: 페이지 번호(1부터 시작).
            page_count: 페이지당 결과 수.

        Returns:
            ``status``, 페이지 정보, 공시 목록(``list``)을 포함한 딕셔너리.
        """

        if corp_code is not None:
            _require_corp_code(corp_code)
        if page_no < 1 or page_count < 1:
            raise ValueError("page_no와 page_count는 1 이상이어야 합니다.")
        return await self._request_json(
            DISCLOSURE_LIST_ENDPOINT,
            {
                "corp_code": corp_code,
                "bgn_de": bgn_de,
                "end_de": end_de,
                "last_reprt_at": last_reprt_at,
                "pblntf_ty": pblntf_ty,
                "pblntf_detail_ty": pblntf_detail_ty,
                "corp_cls": corp_cls,
                "sort": sort,
                "sort_mth": sort_mth,
                "page_no": page_no,
                "page_count": page_count,
            },
        )

    async def get_single_accounts(
        self,
        corp_code: str,
        bsns_year: str,
        reprt_code: str,
    ) -> dict[str, Any]:
        """단일회사 주요계정(``fnlttSinglAcnt.json``)을 조회한다.

        Args:
            corp_code: 기업 고유번호 8자리.
            bsns_year: 사업연도 4자리.
            reprt_code: ``11013``(1분기), ``11012``(반기), ``11014``(3분기),
                ``11011``(사업보고서).

        Returns:
            재무상태표·손익계산서 주요계정과 기간별 금액을 담은 딕셔너리.
        """

        return await self._request_json(
            SINGLE_ACCOUNT_ENDPOINT,
            _require_report_params(corp_code, bsns_year, reprt_code),
        )

    async def get_single_indices(
        self,
        corp_code: str,
        bsns_year: str,
        reprt_code: str,
        idx_cl_code: str,
    ) -> dict[str, Any]:
        """단일회사 주요 재무지표(``fnlttSinglIndx.json``)를 조회한다.

        Args:
            corp_code: 기업 고유번호 8자리.
            bsns_year: 사업연도 4자리.
            reprt_code: 보고서 코드(``11013``, ``11012``, ``11014``, ``11011``).
            idx_cl_code: 지표분류코드. 수익성 ``M210000``, 안정성 ``M220000``,
                성장성 ``M230000``, 활동성 ``M240000``.

        Returns:
            공식 재무지표 목록을 포함한 딕셔너리.
        """

        if not idx_cl_code:
            raise ValueError("idx_cl_code는 필수입니다.")
        return await self._request_json(
            SINGLE_INDEX_ENDPOINT,
            {
                **_require_report_params(corp_code, bsns_year, reprt_code),
                "idx_cl_code": idx_cl_code,
            },
        )

    async def get_single_accounts_all(
        self,
        corp_code: str,
        bsns_year: str,
        reprt_code: str,
        fs_div: str,
    ) -> dict[str, Any]:
        """단일회사 전체 재무제표(``fnlttSinglAcntAll.json``)를 조회한다.

        Args:
            corp_code: 기업 고유번호 8자리.
            bsns_year: 사업연도 4자리.
            reprt_code: 보고서 코드.
            fs_div: ``OFS``(별도) 또는 ``CFS``(연결).

        Returns:
            BS, IS, CIS, CF, SCE 계정과 기간별 금액을 포함한 딕셔너리.
        """

        if fs_div not in FS_DIVISIONS:
            raise ValueError("fs_div는 'OFS' 또는 'CFS'여야 합니다.")
        return await self._request_json(
            SINGLE_ACCOUNT_ALL_ENDPOINT,
            {
                **_require_report_params(corp_code, bsns_year, reprt_code),
                "fs_div": fs_div,
            },
        )

    async def get_document(self, rcept_no: str) -> bytes:
        """공시 원문을 ZIP 바이너리로 반환한다.

        Args:
            rcept_no: 공시검색 API에서 받은 접수번호 14자리.

        Returns:
            공시 원문 ZIP 바이너리. 파일 저장·압축 해제는 호출자 책임이다.
        """

        if len(rcept_no) != 14 or not rcept_no.isdigit():
            raise ValueError("rcept_no는 숫자 14자리여야 합니다.")
        try:
            # 현재 실서버에서 정상적으로 ZIP을 반환하는 XML 출력 형식을 우선 사용한다.
            return await self._request_binary(
                DOCUMENT_ENDPOINT,
                {"rcept_no": rcept_no},
            )
        except OpenDartApiError as exc:
            # 서버 설정에 따라 JSON 출력 형식만 허용되는 경우를 대비한다.
            if exc.status not in {"101", "014"}:
                raise
            return await self._request_binary(
                DOCUMENT_JSON_ENDPOINT,
                {"rcept_no": rcept_no},
            )

    async def get_multi_accounts(
        self,
        corp_code: str,
        bsns_year: str,
        reprt_code: str,
    ) -> dict[str, Any]:
        """회사간 주요계정 비교(``fnlttMultiAcnt.json``) 결과를 조회한다.

        Args:
            corp_code: 비교 대상 공시회사 고유번호 8자리.
            bsns_year: 비교할 사업연도 4자리.
            reprt_code: 비교할 보고서 코드.

        Returns:
            회사간 주요계정 비교 목록과 원본 응답 상태를 담은 딕셔너리.
        """

        return await self._request_json(
            MULTI_ACCOUNT_ENDPOINT,
            _require_report_params(corp_code, bsns_year, reprt_code),
        )

    async def get_multi_indices(
        self,
        corp_code: str,
        bsns_year: str,
        reprt_code: str,
        stacnt_code: str = "M210000",
        idx_cl_code: str = "M210000",
    ) -> dict[str, Any]:
        """회사간 주요 재무지표 비교 API를 조회한다.

        Args:
            corp_code: 비교 대상 공시회사 고유번호 8자리.
            bsns_year: 비교할 사업연도 4자리.
            reprt_code: 비교할 보고서 코드.
            stacnt_code: 회사간 재무지표 요청의 기준 코드.
            idx_cl_code: 수익성 ``M210000``, 안정성 ``M220000``,
                성장성 ``M230000``, 활동성 ``M240000``.

        Returns:
            회사간 재무지표 비교 결과 딕셔너리.

        Note:
            OpenDART 공식 현재 엔드포인트는 ``fnlttCmpnyIndx.json``이다.
            ImportantList.md의 ``fnlttMultiIndx`` 표기는 이 메서드에서 공식
            엔드포인트로 매핑한다.
        """

        if not stacnt_code or not idx_cl_code:
            raise ValueError("stacnt_code와 idx_cl_code는 필수입니다.")
        return await self._request_json(
            MULTI_INDEX_ENDPOINT,
            {
                **_require_report_params(corp_code, bsns_year, reprt_code),
                "stacnt_code": stacnt_code,
                "idx_cl_code": idx_cl_code,
            },
        )

    async def get_xbrl_taxonomy(self, sj_div: str) -> dict[str, Any]:
        """XBRL 재무제표 계정 체계(``xbrlTaxonomy.json``)를 조회한다.

        Args:
            sj_div: 재무제표 구분 코드. 예: ``BS1``, ``IS1``, ``CF1``, ``SCE1``.

        Returns:
            계정 ID, 계정명, 한·영 표시명, 데이터 유형을 포함한 딕셔너리.
        """

        if not sj_div:
            raise ValueError("sj_div는 필수입니다.")
        return await self._request_json(XBRL_TAXONOMY_ENDPOINT, {"sj_div": sj_div})

    async def get_xbrl_file(
        self,
        rcept_no: str,
        reprt_code: str,
    ) -> bytes:
        """XBRL 원본(``fnlttXbrl.xml``) ZIP을 반환한다.

        Args:
            rcept_no: 공시검색 결과의 접수번호. OpenDART 원문 규격상 숫자 값이다.
            reprt_code: 보고서 코드.

        Returns:
            XBRL 원본 파일이 담긴 ZIP 바이너리.
        """

        if not rcept_no.isdigit():
            raise ValueError("rcept_no는 숫자 문자열이어야 합니다.")
        if reprt_code not in REPORT_CODES:
            raise ValueError(f"reprt_code는 {sorted(REPORT_CODES)} 중 하나여야 합니다.")
        return await self._request_binary(
            XBRL_FILE_ENDPOINT,
            {"rcept_no": rcept_no, "reprt_code": reprt_code},
        )


async def call_important_api(
    endpoint: str,
    params: Mapping[str, str | int | None] | None = None,
    api_key: str | None = None,
) -> dict[str, Any]:
    """MCP에서 동적으로 ImportantList JSON API를 호출할 수 있는 진입점.

    Args:
        endpoint: ``company.json`` 또는 ``/api/company.json`` 같은 엔드포인트.
        params: API별 파라미터. 인증키(``crtfc_key``)는 자동으로 추가된다.
        api_key: 선택적 OpenDART 인증키.

    Returns:
        OpenDART 정상 JSON 응답 딕셔너리.
    """

    async with OpenDartImportantClient(api_key=api_key) as client:
        return await client.call_json_api(endpoint, params)


async def get_company_financial_data(
    company_name: str,
    history_count: int = 1,
    fs_div: str = "CFS",
    api_key: str | None = None,
    database_url: str | None = None,
    include_raw: bool = False,
) -> dict[str, Any]:
    """MCP에서 회사명으로 최신·과거 재무보고서를 바로 조회하는 진입점.

    Args:
        company_name: 사용자가 전달한 회사명.
        history_count: 최신 보고서 포함 과거 보고서 개수.
        fs_div: ``CFS``(연결) 또는 ``OFS``(별도).
        api_key: 선택적 OpenDART 인증키.
        database_url: 선택적 CorpCode MySQL URL.

    Returns:
        CorpCode 식별정보, 기업개황, 보고서별 재무 API 원본 응답을 포함한 딕셔너리.
    """

    async with OpenDartImportantClient(api_key=api_key) as client:
        full_result = await client.get_company_financial_data(
            company_name=company_name,
            history_count=history_count,
            fs_div=fs_div,
            database_url=database_url,
            include_raw=include_raw,
        )

    # MCP/LLM 기본 응답은 검증이 끝난 compact DTO만 전달한다.
    # 내부에서는 기존과 동일하게 RAW -> normalize -> validation -> conflict
    # -> canonical -> compact 전체 파이프라인을 수행하므로 정확성 로직은 유지된다.
    # include_raw=True는 디버깅/개발용으로 기존 전체 결과를 그대로 반환한다.
    if include_raw:
        return full_result

    compact_reports = [
        report_result.get("compact")
        for report_result in full_result.get("reports", [])
        if report_result.get("compact") is not None
    ]

    return {
        "response_mode": "compact",
        "company": {
            "corp_code": (full_result.get("company") or {}).get("corp_code"),
            "corp_name": (full_result.get("company") or {}).get("corp_name")
            or (full_result.get("company") or {}).get("corp_name_eng"),
        },
        "reports": compact_reports,
    }


__all__ = [
    "OpenDartApiError",
    "OpenDartImportantClient",
    "call_important_api",
    "get_company_financial_data",
    "get_api_key",
    "normalize_account_item",
    "normalize_index_item",
    "validate_normalized_accounts",
    "build_canonical_metrics",
    "get_validated_canonical_metrics",
    "classify_canonical_metric_for_report",
]
