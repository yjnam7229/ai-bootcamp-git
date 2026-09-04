# Request Body의 다양한 옵션
#  - FastAPI의 Body() 함수와 옵션들

from fastapi import FastAPI, Body

app = FastAPI()

# curl 명령 테스트 방법
# - curl –X POST "http://127.0.0.1:8000/advanced_items/" –H "Content-Type: application/json" –d "{\"key\": \"value\"}"
# 결과: 서버는 {"item": {"key": "value"}} 형태로 응답. 예제의 alias는 실제코드에서 사용되지 않으므로, {"key": "value"} 형태로 Body 전송.
# FastAPI의 자동 문서화 기능을 통해 제목, 설명등을 http://127.0.0.1:8000/docs에서 확인 가능.
@app.post("/advanced_items/")
def create_advanced_item(item: dict = Body(
    default=None,               # 필드의 기본값 설정. 선택적 필드로 만들기 위해 None 사용
    example={"key": "value"},   # 문서에서 보여줄 예시 값 설정
    alias="item_alias",         # 필드의 별칭 설정(실제 사용되지 않음)
    title="Sample Item",        # 문서에서 보여줄 Body의 제목
    description="This is a sample item", # Body에 대한 상세 설명
    deprecated=False)):         # 필드의 사용 중단 여부 표시
    return {"item": item}

# 실행: uvicorn main:app --reload