#Pydantic 모델과 FastAPI 코드 예제
# Pydantic 모델은 자동 유효성 검사 (422 Unprocessable Entity : 요청은 이해 했으나, 요청된 작업을 수행할 수 없음 예: 데이터 유효성 검증 실패)

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):  # Pydantic 모델 정의
    name: str
    price: float
    is_offer: bool = None

# curl을 사용한 Pydantic 테스트
# 1. POST 메소드 테스트
# curl –X POST “http://127.0.0.1:8000/items/” –H “accept:application/json” –H “Content-Type: application/json” –d “{\“name\”: \"Bread\", \"price\":3.5, \"is_offer\":true}” 
#    -> 결과 : {"item": {“name”: "Bread", "price":3.5, "is_offer":true}} 
# Swagger UI 접근 :  http://127.0.0.1:8000/docs  

# 2. 데이터 유효성 검사 실패 시
# curl –X POST “http://127.0.0.1:8000/items/” –H “accept:application/json” –H “Content-Type: application/json” –d “{\“name\”: \"Bread\", \"price\":\"invalid\", \"is_offer\":true}” 
#    -> 결과 : FastAPI에서 유효하지 않은 데이터(price가 문자열)로 인한 에러 반환 
@app.post("/items/")
def create_item(item: Item):
    return {"item": item.model_dump()}  # Pydantic 모델을 API에 사용