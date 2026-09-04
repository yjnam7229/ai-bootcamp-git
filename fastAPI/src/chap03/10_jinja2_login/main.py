from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/login")
def login_form(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="loginForm.html"  # 응답 페이지(FastAPI 안에 적재함)
    )


# pip install python-multipart
@app.post("/loginProcess")
def login_process(id: str = Form(...), pw: str = Form(...)):
    return {"id": id, "pw": pw}