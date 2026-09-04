from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI()
app.mount("/img", StaticFiles(directory="static/img"), name="img") # 특정 경로(URL)에 폴더나 다른 어플리케이션을 연결하는 작업
templates = Jinja2Templates(directory="templates")

# http://localhost:8000/
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )
