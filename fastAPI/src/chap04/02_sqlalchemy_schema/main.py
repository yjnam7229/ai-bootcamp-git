from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# SQLAlchemy에서 모델 클래스의 베이스 클래스를 생성함.
Base = declarative_base()

class User(Base):
    # 데이터베이스 테이블 이름을 'users'로 설정.
    __tablename__ = 'users'
    
    # 'id' 필드는 정수형 기본 키로, 자동 증가를 위한 설정이 추가되어 있음.
    id = Column(Integer, primary_key=True, autoincrement=True, comment="기본 키")
    
    # 'username' 필드는 최대 길이 50의 문자열로, 유니크하며 null 값을 허용하지 않고, 인덱싱되어 있음.
    username = Column(String(50), unique=True, nullable=False, index=True, comment="사용자 이름")
    
    # 'email' 필드는 최대 길이 120의 문자열로, 유니크하며 null 값을 허용하지 않음.
    email = Column(String(120), unique=True, nullable=False, comment="이메일 주소")
    
    # 'is_active' 필드는 불리언 타입으로, 사용자 계정의 활성 상태를 나타냄.
    # 기본값은 True.
    is_active = Column(Boolean, default=True, comment="활성 상태")
    
    # 'created_at' 필드는 DateTime 타입으로, 레코드 생성 시각을 나타냄.
    # 기본값으로 현재 시각(UTC)이 사용됨.
    created_at = Column(DateTime, default=datetime.now(datetime.timezone.utc), comment="생성 타임스탬프")
    
    # 'grade' 필드는 Float 타입으로, 사용자 등급이나 점수 등을 저장할 수 있음.
    grade = Column(Float, comment="사용자 등급")
    
    # 'parent_id' 필드는 외래 키로, 다른 테이블의 기본 키와 연결됨.
    # 여기서는 'parents' 테이블의 'id' 필드를 참조함.
    parent_id = Column(Integer, ForeignKey('parents.id'), comment="상위 ID")