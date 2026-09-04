# config.py
# Pydantic Settings 기반 환경변수 & SQLAlchemy Engine/Session
import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# 프로젝트 기본 경로
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

class Settings(BaseSettings):
    PROJECT_NAME: str = "SalesGPT"
    
    # API Keys
    OPENAI_API_KEY: str
    DART_API_KEY: str
    
    # Models
    DEFAULT_LLM_MODEL: str = "gpt-5-nano"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    
    # Paths & Databases
    DATABASE_URL: str = f"sqlite:///{DATA_DIR / 'app.db'}"
    CHROMA_PERSIST_DIR: str = str(DATA_DIR / "chroma")
    CHECKPOINT_DB_PATH: str = str(DATA_DIR / "checkpoints.sqlite")

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

# SQLAlchemy 2.0 Engine & Session
engine = create_engine(
    settings.DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()