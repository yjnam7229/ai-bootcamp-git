# FastAPI 응답 모델
# 3. List 응답 모델

from typing import List
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str

# curl 테스트 명령
# curl -X GET "http://127.0.0.1:8000/items/"
@app.get("/items/", response_model=List[Item])
async def get_items():
    return [{"name": "Item 1"}, {"name": "Item 2"}]

# 실행: uvicorn main:app --reload