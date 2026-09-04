# FastAPI 응답클래스
# 3. PlainTextResponse : 텍스트 형식의 데이터 반환. 
#                        로깅메시지, 간단한 안내 문구등의 텍스트 반환에 적합.

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

app = FastAPI()

# curl 테스트 명령
# - curl -X GET "http://127.0.0.1:8000/text"
# 예상결과: This is Plain Text 형태의 단순 텍스트 응답
@app.get("/text", response_class=PlainTextResponse)
def read_text():
    return "This is Plain Text"

# 실행: uvicorn main:app --reload