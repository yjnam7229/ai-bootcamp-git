from fastapi import FastAPI, Request
from starlette.middleware.sessions import SessionMiddleware
from database import Base, engine
from controller import router
from fastapi.templating import Jinja2Templates

app = FastAPI()

# SessionMiddleware 추가
app.add_middleware(SessionMiddleware, secret_key='your-secret-key')
Base.metadata.create_all(bind=engine)
app.include_router(router)   # app를 기능별로 router 이름으로 분리(서버의 모듈을 router로 기능별로 정의)
templates = Jinja2Templates(directory='templates')

@app.get('/')
async def read_root(request: Request):
    return templates.TemplateResponse(request, 'home.html')


