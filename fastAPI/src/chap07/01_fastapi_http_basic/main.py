# main.py
# 인증(Authentication) : 사용자가 누구인지 확인하는 과정
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials

# FastAPI 객체 생성
app = FastAPI()
security = HTTPBasic()

def get_current_username(credentials: HTTPBasicCredentials=Depends(security)):  # Depends 의존성 기능
   if credentials.username != 'alice' or credentials.password != 'password':
      raise Exception(status_code=401, detail='Unauthorized')
   
   return credentials.username
    

@app.get('/users/me')
def read_current_user(username:str=Depends(get_current_username)):
   return {'username': username}

# HttpBasic는 기본 인증 방식을 구현함
# get_current_username 함수는 사용자 이름과 비밀번호를 검증함
# 잘못된 인증 정보의 경우 HTTP 401 에러를 반환
# /users/me 엔드포인트는 인증된 사용자만 접근할 수 있음