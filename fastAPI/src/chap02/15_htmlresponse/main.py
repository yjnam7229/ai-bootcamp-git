# FastAPI 응답클래스
# 2. HTMLResponse : HTML 형식의 데이터 반환.

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

# curl 테스트 명령
# - curl -X GET "http://127.0.0.1:8000/html"
# 예상결과: <h1>This is HTML</h1>
@app.get("/html", response_class=HTMLResponse)
def read_html():
    return "<h1>This is HTML</h1>"

# 실행: uvicorn main:app --reload