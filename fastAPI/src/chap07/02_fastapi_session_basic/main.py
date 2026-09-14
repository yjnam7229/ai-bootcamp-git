# main.py
from fastapi import FastAPI, Request
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()

# 세션 미들웨어 추가, 'verysecret'는 실제 사용 시 안전한 키로 교체해야 합니다.
app.add_middleware(SessionMiddleware, secret_key='your-secret-key')

# async/await 키워드로 정의 되지 않으면 비동기 방식이 아님
# 확장성을 위해 모든 함수를 async 키워드를 붙여서 정의,  ★async는 await 키워드를 만났을 때 동작하는 방식
# 세션 설정
@app.post('/set/')
async def set_session(request: Request):   # Request : 사용자의 모든 정보가 담긴 객체
    request.session['username'] = 'john'   # session 영역안에 데이터 삽입
    return {'message': 'Session value set' }

# 세션 조회
@app.get('/get/')
async def get_session(request: Request):
    username = request.session.get('Username', 'Guest')
    return {'username': username}