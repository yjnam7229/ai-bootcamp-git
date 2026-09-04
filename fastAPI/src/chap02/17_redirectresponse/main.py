# FastAPI 응답클래스
# 4. RedirectResponse : 클라이언트를 다른 URL로 리디렉션.
#                       사용자를 다른 페이지로 유도하거나 경로를 변경할 때 사용.

from fastapi import FastAPI
from fastapi.responses import RedirectResponse, PlainTextResponse

app = FastAPI()


# curl 테스트 명령
# - curl -X GET "http://127.0.0.1:8000/redirect" -L
#   -L 옵션은 리디렉션을 따르도록 설정함 
# 예상결과: /redirect 경로 요청은 /text 경로로 리디렉션되며, "This is Plain Text"라는 응답을 받음.
@app.get("/redirect")
def read_redirect():
    return RedirectResponse(url="/text")  # 재요청

@app.get("/text", response_class=PlainTextResponse)
def read_text():
    return "This is Plain Text"

# 실행: uvicorn main:app --reload