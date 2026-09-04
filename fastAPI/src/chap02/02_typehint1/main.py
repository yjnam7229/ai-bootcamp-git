# 기본 타입 힌트 사용
from fastapi import FastAPI

app = FastAPI()

# 경로 매개변수 예시: item_id: int
# http://127.0.0.1:8000/items/123 -> 출력: {"item_id": 123}
# http://127.0.0.1:8000/items/fastapi -> 오류: item_id가 int가 아님
@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}


# 쿼리 매개변수 예시: data: str = "HelloFastApi"
# http://127.0.0.1:8000/getdata/?data=somequery -> 출력: {"data": somequery}
# http://127.0.0.1:8000/getdata/ -> 출력: {"data": HelloFastApi}
# http://127.0.0.1:8000/getdata/?data=1.1 -> 출력: {"data": "1.1"} (문자열로 처리)
@app.get("/getdata/")
def read_items(data: str = "HelloFastApi"):
    return {"data": data}


# 실행: uvicorn main:app --reload