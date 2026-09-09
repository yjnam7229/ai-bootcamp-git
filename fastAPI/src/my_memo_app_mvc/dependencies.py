# dependencies.py
from passlib.context import CryptContext
from database import SessionLocal # database.py

# 패스워드 Hash 알고리즘을 적용 -> 암복호화
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# 사용자 입력 패스워드 hash(암호화/복호회)
def get_password_hash(password: str):
    return pwd_context.hash(password)

# 패스워드 일치 여부 검증, plain_password : 사용자 입력 패스워드
def verify_password(plain_password, hash_password):   
    return pwd_context.verify(plain_password, hash_password)

# 데이터베이스 연결 sessionmaker
# 데이터베이스 세션을 생성하고 관리하는 의존성 함수 정의
# Depends(함수) 방식
def get_db():
    db = SessionLocal()
    try:
        yield db    # yield : 제너레이터 함수(iterator 함수, 데이터를 하나 하나씩 꺼내옴)
    finally:
        db.close()        
