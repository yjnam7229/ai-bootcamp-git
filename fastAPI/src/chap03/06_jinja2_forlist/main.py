from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from typing import List

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# http://localhost:8000/dynamic_items/?item_list=apple,banana,cherry
@app.get("/dynamic_items/")
def dynamic_items(request: Request, item_list: str = ""):

    items = item_list.split(",")
    
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"items": items}
    )
