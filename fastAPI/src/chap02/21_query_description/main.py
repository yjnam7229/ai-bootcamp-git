# Query 클래스 사용 예: description
# 정의: Query Parameter에 대한 상세한 설명을 추가하는 옵션.
# 기능: API 문서화 도구에서 파라미터 옆에 표시. 사용자의 이해를 돕기 위해 사용.

from fastapi import FastAPI, Query

app = FastAPI()

# 설명: /info/ 경로에서 info라는 Query Parameter를 받으며, 이 파라미터에 "정보를 입력해 주세요."라는 설명을 추가.
# 테스트 방법
# - Swagger UI 접속: http://127.0.0.1:8000/docs 방문.
# - 확인사항: /info/ 엔드포인트에서 info 파라미터 옆에 상세 설명 표시.
@app.get("/info/")
def read_info(info: str = Query(None, description="정보를 입력해 주세요.")):
    return {"info": info}

# 실행: uvicorn main:app --reload