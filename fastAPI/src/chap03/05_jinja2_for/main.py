from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# http://localhost:8000/items
@app.get("/items")
def read_items(request: Request):

    my_items = ["apple", "banana", "cherry"]
    
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"items": my_items}
    )
  
