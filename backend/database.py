# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# SQLite 데이터베이스 파일 이름 (프로젝트 폴더에 db 파일이 생깁니다)
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql.db"

# 데이터베이스 엔진 생성
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# DB 세션(접속창구) 생성기
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)