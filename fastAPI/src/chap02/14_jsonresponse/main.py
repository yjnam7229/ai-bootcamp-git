# FastAPI 응답클래스
# 1. JSONResponse : Python 딕셔너리나 Pydantic 모델을 JSON 문자열로 변환하여 반환.

from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

# curl 테스트 명령
# - curl -X GET "http://127.0.0.1:8000/json"
# 예상결과: {"msg": "This is JSON"} 형태의 JSON 응답.
@app.get("/json", response_class=JSONResponse)
def read_json():
    return {"msg": "This is JSON"}

# 실행: uvicorn main:app --reload