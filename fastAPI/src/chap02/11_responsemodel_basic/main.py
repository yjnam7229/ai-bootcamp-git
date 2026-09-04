# FastAPI 응답 모델
# 1. 기본 응답 모델

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float

# curl을 사용한 테스트
# curl -X GET "http://127.0.0.1:8000/item/"
# 예상 결과: {"name":"milk", "price:3.5"} 형태의 JSON 응답
@app.get("/item/", response_model=Item)
def get_item():
    return {"name": "milk", "price": 3.5}