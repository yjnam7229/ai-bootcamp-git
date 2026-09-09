# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# 데이터베이스 생성
# CREATE DATABASE my_memo_app DEFAULT CHARSET  utf8mb4 COLLATE  utf8mb4_general_ci;
DATABASE_URL = "mysql+pymysql://root:admin1234@localhost:3306/my_memo_app"
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# SQLAlchemy의 Base 클래스를 상속받아 모델의 기본 클래스를 생성함.
Base = declarative_base()