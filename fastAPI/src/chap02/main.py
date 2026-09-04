# FastAPI의 HTTPException 클래스

from fastapi import FastAPI, HTTPException

app = FastAPI()

# curl -X GET "http://127.0.0.1:8000/items/42"
@app.get("/items/{item_id}")
def read_item(item_id: int):
    if item_id == 42:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"item_id": item_id}

# 실행: uvicorn main:app --reload