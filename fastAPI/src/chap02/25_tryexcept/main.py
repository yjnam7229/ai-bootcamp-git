# 예외 처리(Exception Handling) 상세 설명

from fastapi import FastAPI, HTTPException

app = FastAPI()


# curl 명령을 이용한 테스트 방법
# . curl -X GET "http://127.0.0.1:8000/items/-1"
# 결과: 400 Bad Request 상태코드와 "음수는 허용되지 않습니다." 오류 메시지 반환
@app.get("/items/{item_id}")
def read_item(item_id: int):
    try:
        if item_id < 0:
            raise ValueError("음수는 허용되지 않습니다.")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# 실행: uvicorn main:app --reload