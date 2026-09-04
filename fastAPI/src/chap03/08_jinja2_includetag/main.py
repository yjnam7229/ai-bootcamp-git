from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# http://localhost:8000/include_example
@app.get("/include_example")
def include_example(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )