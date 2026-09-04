# 고급 타입 힌트 사용
# 목적: typing 모듈의 List, Dict 등을 사용하여 복잡한 데이터 구조 표현

from fastapi import FastAPI, Query
from typing import List, Dict, Tuple, Set, Any, Optional, Union, Callable

app = FastAPI() 


# List 데이터 타입을 쿼리 매개변수로 받는 라우트 예제.


# List 타입 쿼리 매개변수 테스트
# - http://127.0.0.1:8000/items/?q=1&q=2&q=3 -> 결과: {"q": [1, 2, 3]}

# 타입 불일치 시 에러 테스트
# - http://127.0.0.1:8000/items/?q=하나&q=둘&q=셋 -> 결과: 타입에러(정수가 아닌 문자열 입력)


# List[int] = Query([]) : 리스트 자료형 쿼리 매개변수.
# Query는 쿼리 매개변수의 기본값 설정 및 유효성 검사에 사용됨.
# Query([])는 해당 쿼리 매개변수가 필수가 아님을 나타내고, 기본값으로 빈 리스트를 설정함.
# List 타입 힌트는 반드시 Query()와 함께 사용해야 됨.

# HTTP POST 요청 테스트
# curl –X POST “http://127.0.0.1:8000/create-item/” –H “accept:application/json” –H “Content-Type: application/json” –d “{\“name\”: 1}” 
#    -> 결과 : {“name”: 1} 형태로 요청 본문 받고 반환
@app.get("/items/")
async def read_items(q: List[int] = Query([])): # 빈 리스트를 기본값으로 설정
    return {"q": q}

# @app.get("/dataitems/")
# async def read_items(data: Optional[int] = None): # Optional[int] = None 초기화 반드시 필요
#     return data       # 브라우저는 null을 반환

# http://127.0.0.1:8000/dataitems/?data=True 또는 http://127.0.0.1:8000/dataitems/?data=123  : 호출 url
# @app.get("/dataitems/")
# async def read_items(data: Union[int, bool]): # Union 타입
#     return data   


# http://127.0.0.1:8000/dataitems/?text=Hellow FastAPI  : 호출 url
# Callable 타입
def uppercase(text: str) -> str:
    return text.upper()

@app.get("/dataitems/")
async def convert_text(
    text: str,
    converter: Callable[[str], str] = uppercase
):
    return {"result": converter(text)}


# Dict 데이터 타입을 요청 바디로 받는 라우트 예제
# item: Dict[str, int] : 딕셔너리 자료형 요청 본문
@app.post("/create-item/")
async def create_item(item: Dict[str, int]): # item: Any
    return item


# # 사용자 정의 타입
# class Item(BaseModel):
#     name: str
#     price: int

# @app.post("/items/")
# async def create_items(items: list[Item]):
#     return items

# # 요청
# [
#   {
#     "name": "노트북",
#     "price": 1500000
#   },
#   {
#     "name": "마우스",
#     "price": 30000
#   }
# ]


# 실행: uvicorn main:app --reload