# controller.py
from fastapi import APIRouter, FastAPI, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from models import User, Memo
from schemas import UserCreate, UserLogin, MemoCreate, MemoUpdate

from dependencies import get_db, get_password_hash, verify_password  # dependencies.py

router = APIRouter()  # FastAPI와 동일한 역할
templates = Jinja2Templates(directory='templates')
# app = FastAPI()

 # 회원 가입
# UserCreate 자체적으로 유효성 검증(pydantic)
@router.post('/signup')
async def signup(signup_data: UserCreate, db: Session=Depends(get_db)): 
    # username 중복 체크
    existing_user = db.query(User).filter(User.username == signup_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail='이미 동일한 사용자 이름이 가입되어 있습니다.')
    
    hashed_password = get_password_hash(signup_data.password)  # 패스워드 암복호화
    new_user = User(username=signup_data.username, email=signup_data.email, hashed_password=hashed_password)

    db.add(new_user)
    try:
        db.commit()
    except Exception as e:   
        print(e) 
        raise HTTPException(status_code=500, detail='회원 가입이 실패했습니다. 가입한 내용을 확인해 보세요.')
        
    db.refresh(new_user)
    return {'message:', '회원 가입이 성공 했습니다.'}

# 로그인
@router.post('/login')
async def login(request: Request, signin_data: UserLogin, db: Session=Depends(get_db)):
    user = db.query(User).filter(User.username == signin_data.username).first()
    if user and verify_password(signin_data.password, user.hashed_password):
        request.session['username'] = user.username   # 쿠키의 저장소에 보관된 데이터 -> session에 전달
        return {'message:', 'Logged in successfully'}
    else:
        raise HTTPException(status_code=401, detail='Invalid credentials')

# 로그아웃
@router.post('/logout')
async def logout(request: Request):
    request.session.pop('username', None)  # pop() 꺼내옴 -> 버림
    return {'message': 'Logged out successfully'}


# 메모 생성(CRUD)
@router.post('/memos/')
async def create_memo(request:Request, memo: MemoCreate, db: Session=Depends(get_db)):
    username = request.session.get('username')
    if username is None:
            raise HTTPException(status_code=401, detail='Not authorized')

    user = db.query(User).filter(User.username == username).first()
    if user is None:
            raise HTTPException(status_code=404, detail='User not found')

    new_memo = Memo(user_id=user.id, title=memo.title, content=memo.content)
    db.add(new_memo)
    db.commit()
    db.refresh(new_memo)
    return new_memo
    # return ({'id': new_memo.id, 'title': new_memo.title, 'content': new_memo.content})

# 메모 조회(login한 사용자의 메모만 조회)
@router.get('/memos/')
async def list_memos(request: Request, db: Session=Depends(get_db)):
    username = request.session.get('username')
    if username is None:
        raise HTTPException(status_code=401, detail='Not authorized')

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail='User not found')

    # 로그인한 사용자가 작성한 메모만 가져옴
    memos = db.query(Memo).filter(Memo.user_id == user.id).all() 
    return templates.TemplateResponse(request, 'memos.html', 
                                      {'memos': memos, 'username': username})

    # return [{'id': memo.id,
    #          'title': memo.title,
    #          'content': memo.content} for memo in memos]  # List 자료구조


# 메모 수정
@router.put('/memos/{memo_id}')
async def update_memo(request: Request, memo_id: int, memo: MemoUpdate, db: Session=Depends(get_db)):
    # 로그인 여부 체크
    username = request.session.get('username')
    if username is None:
            raise HTTPException(status_code=401, detail='Not authorized')
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
            raise HTTPException(status_code=404, detail='User not found')

    db_memo = db.query(Memo).filter(Memo.user_id == user.id, Memo.id == memo_id).first()

    if db_memo is None:
        return {'error': 'Memo not found'}
    
    if memo.title is not None:
        db_memo.title = memo.title
    if memo.content is not None:
        db_memo.content = memo.content

    db.commit()
    db.refresh(db_memo)       
    return db_memo         
    # return ({'id': db_memo.id, 'title': db_memo.title, 'content': db_memo.content})

# 메모 삭제 
@router.delete('/memos/{memo_id}')
async def delete_memo(request: Request, 
                      memo_id: int,
                      db: Session=Depends(get_db) 
                      ):

    # check = check_user_info()

    # 로그인 여부 체크
    username = request.session.get('username')
    if username is None:
            raise HTTPException(status_code=401, detail='Not authorized')
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
            raise HTTPException(status_code=404, detail='User not found')

    db_memo = db.query(Memo).filter(Memo.user_id == user.id, Memo.id == memo_id).first()
    if db_memo is None:
        return {'error': 'Memo not found.'}
    
    db.delete(db_memo)
    db.commit()
    return {'message': 'Memo deleted.'}


@router.get("/about")
async def about():
    return {"message":"이것은 마이 메모 앱의 소개 페이지입니다."}

