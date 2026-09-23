"""Download and parse the OpenDART corporation-code ZIP file."""

import json
import os
import zipfile
from io import BytesIO
from pathlib import Path
from xml.etree import ElementTree as ET

import requests


API_URL = "https://opendart.fss.or.kr/api/corpCode.xml"


def get_api_key() -> str:
    """Read the API key without storing it in source code."""
    api_key = os.getenv("DART_API_KEY") or os.getenv("OPENDART_API_KEY")
    if not api_key:
        raise RuntimeError(
            "DART_API_KEY 또는 OPENDART_API_KEY 환경변수가 설정되어 있지 않습니다."
        )
    return api_key


def download_corp_code_zip(api_key: str) -> bytes:
    response = requests.get(
        API_URL,
        params={"crtfc_key": api_key},
        timeout=30,
    )
    response.raise_for_status()

    content = response.content
    if not zipfile.is_zipfile(BytesIO(content)):
        try:
            error = response.json()
        except ValueError:
            error = {"message": response.text[:500]}
        raise RuntimeError(
            f"OpenDART API 오류 "
            f"(status={error.get('status')}): {error.get('message')}"
        )

    return content


def parse_corp_code_zip(zip_bytes: bytes) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []

    with zipfile.ZipFile(BytesIO(zip_bytes)) as archive:
        xml_files = [
            name
            for name in archive.namelist()
            if name.lower().endswith(".xml")
        ]
        if not xml_files:
            raise RuntimeError("ZIP 파일 내부에 XML 파일이 없습니다.")

        root = ET.fromstring(archive.read(xml_files[0]))

    for item in root.findall(".//list"):
        def value(tag: str) -> str:
            return (item.findtext(tag) or "").strip()

        records.append(
            {
                # 앞자리 0을 보존하기 위해 문자열로 저장
                "corp_code": value("corp_code"),
                "corp_name": value("corp_name"),
                "corp_eng_name": value("corp_eng_name"),
                "stock_code": value("stock_code"),
                "modify_date": value("modify_date"),
            }
        )

    return records


def main() -> None:
    zip_path = Path("corpCode.zip")
    json_path = Path("corpCode.json")

    zip_bytes = download_corp_code_zip(get_api_key())
    zip_path.write_bytes(zip_bytes)

    records = parse_corp_code_zip(zip_bytes)
    json_path.write_text(
        json.dumps(records, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"기업 레코드: {len(records)}")
    print(f"ZIP: {zip_path.resolve()} ({zip_path.stat().st_size} bytes)")
    print(f"JSON: {json_path.resolve()} ({json_path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
