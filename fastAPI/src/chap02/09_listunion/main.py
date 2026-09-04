# List와 Union 사용

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Union

app = FastAPI()

class Item(BaseModel):
    name: str         # 문자열 필드
    tags: List[str]   # 문자열 리스트
    variant: Union[int, str]  # 정수 또는 문자열

# curl을 사용한 테스트
# curl –X POST “http://127.0.0.1:8000/items/” –H “accept:application/json” –H “Content-Type: application/json” –d “{\“name\”: \"Laptop\", \"tags\":[\"electronics\", \"office\"], \"variant\":\"Pro\"}”
# 예상 결과: name 필드에 "Laptop", tags 필드에 ["electronics", "office"], variant 필드에 "Pro" 
@app.post("/items/")
def create_item(item: Item):
    return {"item": item.model_dump()}

# 실행: uvicorn main:app --reload