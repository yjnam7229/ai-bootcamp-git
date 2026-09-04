# FastAPI 응답 모델
# 2. Union 응답 모델

from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Cat(BaseModel):
    catname: str #name: str

class Dog(BaseModel):
    dogname: str # name: str

# curl 테스트 명령
# 고양이 데이터 요청
# - curl -X GET "http://127.0.0.1:8000/animal/?animal=cat"

# 개 데이터 요청
# - curl -X GET "http://127.0.0.1:8000/animal/?animal=dog"
@app.get("/animal/", response_model=Union[Cat, Dog])
async def get_animal(animal: str):
    if animal == "cat":
        return {"catname": "Whiskers"} # Cat(name="Whiskers")
    else:
        return {"dogname": "Fido"} # Dog(name="Fido")

# 실행: uvicorn main:app --reload