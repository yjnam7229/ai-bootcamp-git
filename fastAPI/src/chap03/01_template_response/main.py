from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"username": "John"}
    )

# username을 요청에서 받기(경로 파라미터 사용 예제)
# http://127.0.0.1:8000/user/john
@app.get("/user/{username}")
def get_user1(request: Request, username: str):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"username": username}
    )

# username을 요청에서 받기(쿼리 파라미터 사용 예제)
# http://127.0.0.1:8000/user?username=fastAPI
@app.get("/user")
def get_user2(request: Request, username: str = "John"):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"username": username}
    )