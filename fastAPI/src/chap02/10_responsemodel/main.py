# FastAPI 응답 모델
# response_model 문법

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    description: str = None
    price: float

def get_item_from_db(id):
    # 매우 간단한 아이템 반환
    return {
        "name": "Simple Item", 
        "description": "A simple item description", 
        "price": 50.0,
        "dis_price": 45.0
    }
  
@app.get("/items/{item_id}", response_model=Item)
def read_item(item_id: int):
    item = get_item_from_db(item_id)
    return item