# Pydantic의 다양한 문법과 예제

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: float = 0.1

# curl을 사용한 테스트
# curl –X POST “http://127.0.0.1:8000/items/” –H “accept:application/json” –H “Content-Type: application/json” –d “{\“name\”: \"Soap\", \"price\":2.5}” 
@app.post("/items/")
async def create_item(item: Item):
    return {"item": item.model_dump()}