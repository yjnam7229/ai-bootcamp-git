# FastAPI는 웹 프레임워크로서 웹 서버 구축에 다양한 기능을 제공하며, 이 중 템플릿 엔진 지원이 포함됨
# 이 기능은 HTML 파일 내에서 데이터를 동적으로 처리할 수 있도록 해줌
# FastAPI는 Jinja2라는 강력한 템플릿 엔진을 사용하여 HTML 내에서 파이썬 코드를 사용할 수 있게 해줌
# Jinja2는 FastAPI의 템플릿을 취급할 때 요구되는 중요한 패키지

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory='templates')

# 기본 라우팅
# curl http://127.0.0.1:8000/
@app.get('/')
async def read_root(request: Request):
    return templates.TemplateResponse(request, 'home.html')

# 확장 라우팅
@app.get('/about')
async def about():
    return {'message': '이것은 마이 메모 앱의 소개 페이지입니다.'}


# pip install jinja2    