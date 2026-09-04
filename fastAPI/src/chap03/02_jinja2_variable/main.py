from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/safe")
def read_root_safe(request: Request):
    
    my_variable_with_html = "<h1>Hello, FastAPI!</h1>"
    
    return templates.TemplateResponse(
        request=request,
        name="index_with_safe.html",
        context={"my_variable_with_html": my_variable_with_html}
    )