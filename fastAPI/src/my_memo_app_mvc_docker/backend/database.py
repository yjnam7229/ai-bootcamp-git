from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# CREATE DATABASE my_memo_app DEFAULT CHARSET  utf8mb4 COLLATE  utf8mb4_general_ci;

# 데이터베이스 설정을 위한 문자열을 정의. 이 문자열에는 사용자 이름, 비밀번호, 서버 주소, 데이터베이스 이름이 포함되어 있음.
DATABASE_URL = "mysql+pymysql://root:admin1234@db:3306/my_memo_app"
# DATABASE_URL = "mysql+pymysql://root:admin1234@localhost:3306/my_memo_app"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# SQLAlchemy의 모델 기본 클래스를 선언. 이 클래스를 상속받아 데이터베이스 테이블을 정의할 수 있음.
Base = declarative_base()