from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# http://localhost:8000/greet?time_of_day=[morning|afternoon|evening]
# http://127.0.0.1:8000/greet?time_of_day=afternoon
@app.get("/greet")
def greeting(request: Request, time_of_day: str):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"time_of_day": time_of_day}
    )
