# Query 클래스 사용 예: alias
# 예시: 클라이언트가 URL에입력하는 Query Parameter 이름과 서버 내부에서 사용하는 변수명 분리 설정.
# 사용법: Query 클래스의 alias 옵션을 통해 URL의 Query Parameter 이름과 다른 내부 변수명 지정.

from fastapi import FastAPI, Query

app = FastAPI()

# 설명: /items/ 경로에서 search라는 Query Parameter를 internal_query 라는 변수로 처리.
# 테스트 방법
# - cURL 명령: curl -X GET "http://127.0.0.1:8000/items/?search=test"
# 결과: {"query_handled": "test"} 형태의 응답 반환.
# Query 클래스의 alias 기능은 클라이언트와 서버 간의 인터페이스를 유연하게 관리하고, 
# API 설계에서 내부 구현 로직을 추상화하는 데 유용함. 이를 통해 개발자는 보다 깔끔하고 안전한 API를 제공할 수 있음.
@app.get("/items/")
def read_items(internal_query: str = Query(None, alias="search")):
    return {"query_handled": internal_query}

# 실행: uvicorn main:app --reload