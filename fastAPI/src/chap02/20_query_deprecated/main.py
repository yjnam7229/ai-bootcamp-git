# Query 클래스 사용 예: deprecated
# 정의: Query Parameter가 구식이 되었거나 더 이상 사용되지 않음을 표시하는 옵션.
# 기능: API 사용자에게 해당 파라미터를 향후 사용하지 말 것을 권장.

from fastapi import FastAPI, Query

app = FastAPI()

# 설명: /users/ 경로에서 q라는 Query Parameter를 받지만, 
#       deprecated=True 설정으로 이 파라미터의 사용 중단을 권고.
# 테스트 방법
#  - Swagger UI 접속: http://127.0.0.1:8000/docs 방문.
#  - 확인 사항: /users/ 엔드포인트에서 q 파라미터가 사용 중단됨을 표시.
@app.get("/users/")
def read_users(q: str = Query(None, deprecated=True)):
    return {"q": q}

# 실행: uvicorn main:app --reload