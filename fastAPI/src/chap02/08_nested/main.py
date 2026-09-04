# 중첩된 모델

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Image 모델이 Item 모델 안에 포함되어 있음
# Item 모델은 Image 타입의 image 필드를 가짐
class Image(BaseModel): # 이미지에 대한 정보를 담는 Pydantic 모델.
    url: str
    name: str

# 중첩된 자료형 선언
class Item(BaseModel): # 아이템에 대한 정보를 담는 Pydantic 모델로, Image 모델을 image 필드로 포함함.
    name: str
    description: str
    image: Image


# curl을 사용한 테스트
# curl –X POST “http://127.0.0.1:8000/items/” –H “accept:application/json” –H “Content-Type: application/json” –d “{\“name\”: \"Smartphone\", \"description\":\"Latest model\", \"image\":{\"url\":\"http://example.com/image.jpg\", \"name\":\"front_view\"}}”
# 결과: 서버는 요청 데이터를 Item 모델로 변환하고, 유효성을 검사한 후 응답함.
@app.post("/items/")
def create_item(item: Item):
    return {"item": item.model_dump()}

# 실행: uvicorn main:app --reload