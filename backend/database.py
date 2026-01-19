# database.py
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

# SQLite 데이터베이스 파일 이름 (프로젝트 폴더에 db 파일이 생깁니다)
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql.db"

# 데이터베이스 엔진 생성
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})


# WAL 모드 활성화
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")  # 읽기/쓰기 동시성 향상
    cursor.execute("PRAGMA synchronous=NORMAL")  # 쓰기 속도 향상 (안전성 약간 타협)
    cursor.close()


# DB 세션(접속창구) 생성기
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
