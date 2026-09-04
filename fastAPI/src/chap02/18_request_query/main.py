# FastAPI에서의 HTTP Request 정의
# - 주로 Query와 Body() 클래스를 활용하여 세밀한 정의 가능함

from fastapi import FastAPI, Query

app = FastAPI()

# 설명: /users/ 경로에 대한 GET 요청처리. q라는 Query Parameter를 받아, 최대길이 제한을 설정.
# curl 테스트 명령
# - curl -X GET "http://127.0.0.1:8000/users/?q=somequery"
# 결과: /users/ 엔드포인트로 GET 요청을 보내고, q에 "somequery"값을 전달. 서버는 이를 JSON 형태로 반환.
@app.get("/users/")
def read_users(q: str = Query(None, max_length=50)):
    return {"q": q}

# 실행: uvicorn main:app --reload