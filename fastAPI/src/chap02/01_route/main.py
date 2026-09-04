from fastapi import FastAPI

app = FastAPI()

# 기본 라우팅
# curl http://127.0.0.1:8000/
@app.get("/")
def read_root():
    return {"message":"Hello, FastAPI!!!"}

# 경로 매개변수(Path Parameters) - {item_id}가 경로 매개변수
# curl http://127.0.0.1:8000/items/5
@app.get("/items/{item_id}")
def read_item(item_id):
    return {"item_id":item_id}

# 복수의 경로 매개변수 사용 - {item_id}가 경로 매개변수
# curl http://127.0.0.1:8000/users/123/items/foobar
@app.get("/users/{user_id}/items/{item_name}")
def read_user_item(user_id, item_name):
    return {"user_id":user_id, "item_name": item_name}

# 쿼리 매개변수
# /items/?skip=5&limit=7에서 skip과 item이 쿼리 매개변수
# curl "http://127.0.0.1:8000/items/?skip=5&limit=7"
# @app.get("/items/")
# def read_items(skip, limit):
#     return {"skip":skip, "limit":limit}

# curl "http://127.0.0.1:8000/items/    : skip=0, limit=10이 출력
@app.get("/items/")
def read_items(skip = 0, limit = 10):
    return {"skip": skip, "limit": limit}