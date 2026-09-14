from fastapi import FastAPI, Request, HTTPException
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()
# 세션 미들웨어 추가, 'verysecret'는 실제 사용 시 안전한 키로 교체해야 합니다.
app.add_middleware(SessionMiddleware, secret_key='verysecret')

# login 설정
@app.post('/login/')
async def login(request: Request, username: str, password: str):
    if username == 'john' and password == '1234':
        request.session['username'] = username
        return {"message": "Successfully logged in"}
    else:
        raise HTTPException(status_code=401, detail='Invalid credentials')

# login 조회
@app.get('/dashbord')    
async def dashboard(request: Request):
    username = request.session.get('username')
    if not username:
        raise HTTPException(status_code=401, detail='Not autorized')
    return {'message': f'Welcom to the dashbord, {username}'}