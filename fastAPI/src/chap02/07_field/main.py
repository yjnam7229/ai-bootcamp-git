# Pydantic의 필드 제약조건

from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List

app = FastAPI()

# 아래 코드에서 Field 함수의 ...(줄임표, ellipsis)는 필드가 필수임을 나타냄. 
# name과 price는 필수 필드, description은 선택 필드, tag는 선택 필드이며 기본값이 빈 리스트.
class Item(BaseModel):
    name: str = Field(..., title="Item Name", min_length=2, max_length=50) #redoc을 통해 봐야 됨(문서화)
    description: str = Field(None, description="The description of the item", max_length=300)
    price: float = Field(..., gt=0, description="The price must be greater than zero")
    tag: List[str] = Field(default=[], alias="item-tags")

@app.post("/items/")
async def create_item(item: Item):
    return {"item": item.model_dump()}

# 실행: uvicorn main:app --reload