from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI"}

@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}

@app.get("/items/")
def read_items(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}

# POST(Create) 메소드 테스트
# curl –X POST “http://127.0.0.1:8000/items/” –H “Content-Type: application/json” –d “{\“name\”: \"item1\", \"value\":42}” 
#    -> 결과 : {"item":{“name”: "item1", "value":42}}
@app.post("/items/")
def create_item(item: dict):
    return {"item": item}

# PUT(Update) 메소드 테스트
# curl –X PUT "http://127.0.0.1:8000/items/1" –H "accept:application/json" –d "{\"name\": \"updated_item\", \"value\":43}" 
#    -> 결과 : {"item_id":1, "updated_item":{“name”: "updated_item", "value":43}}
@app.put("/items/{item_id}")
def update_item(item_id: int, item: dict):
    return {"item_id": item_id, "updated_item": item}

# DELETE 메소드 테스트
# curl –X DELETE “http://127.0.0.1:8000/items/1” –H “accept:application/json”
#    -> 결과 : {"message": "Item 1 has been deleted"}
@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    return {"message": f"Item {item_id} has been deleted"}


# –H “accept:application/json” : 응답을 json 포맷으로 받았으면 좋겠어 요청
# –H “Content-Type: application/json” : 보내는 데이터가 JSON 형식임