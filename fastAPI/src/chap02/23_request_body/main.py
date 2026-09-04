# FastAPI에서의 Request Body 처리
# - Body() 함수를 사용하여 복잡한 구조의 데이터를 처리하고 관리.
# Request Body 처리 방식
# - 적용 메소드: POST, PUT 메소드에서 주로 사용됨
# - GET 요청: 일반적으로 Body를 포함하지 않으며, Query Parameters 또는 URL 경로를 통해 데이터 전송.

from fastapi import FastAPI, Body

app = FastAPI()

# 설명: POST 메소드를 사용하여 JSON 형식의 데이터를 처리하는 함수를 정의함. Body(...)는 해당 필드가 필수임을 나타냄.
# Request Body 선택적 사용
#   - 선택적 필드: 필수가 아닌 경우 Body(None)을 사용하여 기본값을 None으로 설정할 수 있음.
# curl 명령 테스트 방법
# - curl –X POST "http://127.0.0.1:8000/items/" –H "Content-Type: application/json" –d "{\"key\": \"value\"}"
# 결과: 서버는 클라이언트가 보낸 데이터를 처리하고 JSON 형식으로 응답함.
@app.post("/items/")
def create_item(item: dict = Body(...)):
    return {"item": item}

# 실행: uvicorn main:app --reload