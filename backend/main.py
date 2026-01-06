import threading
import time
from contextlib import asynccontextmanager
from typing import List, Optional, Any
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from database import engine, SessionLocal
from models import Base, Article, Issue, User
from scraper import run_article_crawler
from crud import create_article, create_user, get_user
from ai_processor import process_news_pipeline 

# --- [Pydantic 모델] 프론트엔드에 보낼 데이터 형태 정의 ---
class ArticleResponse(BaseModel):
    id: int
    title: str
    content: Optional[str] = None          # 본문
    publisher: str
    published_at: Optional[datetime]
    url: str
    image_url: Optional[List[str]] = None

    class Config:
        from_attributes = True

class IssueResponse(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    # 통째로 구조화된 JSON 데이터를 보냅니다. (프론트엔드가 받아서 알아서 뿌림)
    analysis_result: Optional[Any] 

    class Config:
        from_attributes = True

# 회원가입 요청 시 받을 데이터
class UserCreateRequest(BaseModel):
    login_id: str
    password_hash: str  # 실제로는 비밀번호 원문을 받아 내부에서 해싱하는 것이 좋지만, 현재 구조에 맞췄습니다.
    user_real_name: Optional[str] = None
    email: Optional[str] = None
    subscribed_categories: Optional[List[str]] = []
    subscribed_keywords: Optional[List[str]] = []
    preferred_time_range: Optional[Any] = None # JSON이나 문자열
    marketing_agree: bool = False

# 클라이언트에게 응답할 데이터 (비밀번호 제외)
class UserResponse(BaseModel):
    login_id: str
    user_real_name: Optional[str] = None
    email: Optional[str] = None
    subscribed_categories: Optional[List[str]] = []
    subscribed_keywords: Optional[List[str]] = []
    preferred_time_range: Optional[Any] = None
    marketing_agree: bool = False
    
    # 시스템이 생성하는 정보 (가입일, 상태 등)
    created_at: Optional[datetime] = None 
    user_status: int = 1 

    class Config:
        from_attributes = True

# --- [백그라운드 워커] 주기적으로 뉴스 수집 & AI 분석 ---
def run_background_worker():
    print("🚀 [System] 백그라운드 워커 가동 시작")
    while True:
        print("\n⏰ [Auto] 뉴스 수집 및 분석 사이클 시작...")
            
        # 1. 뉴스 수집 (DB 연결)
        db = SessionLocal()
        try:
            # 스마트 수집 (중복 만나면 중단)
            # news_list = crawl_breaking_news(limit=20, db_check_session=db)
            news_list = run_article_crawler(["조선일보", "한국일보", "연합뉴스"], False)
            count = 0
            for news in news_list:
                # 기사 db에 저장
                if create_article(db, news):
                    count += 1
                pass
            print(f"   -> {count}개의 신규 기사 저장 완료")
        finally:
            db.close()

        # 2. AI 파이프라인 가동 (신규 기사가 있든 없든, 분석 대기 중인 게 있을 수 있으므로 실행)
        process_news_pipeline()
        
        # 10분(600초) 대기
        print("💤 [Sleep] 10분 대기 중...")
        time.sleep(600)

# --- [FastAPI 앱 설정] ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 앱 시작 시 DB 테이블 생성
    Base.metadata.create_all(bind=engine)
    
    # 백그라운드 스레드 시작
    worker_thread = threading.Thread(target=run_background_worker, daemon=True)
    worker_thread.start()
    
    yield
    print("👋 서버 종료")

app = FastAPI(lifespan=lifespan)

# DB 세션 의존성
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- [API 엔드포인트] ---

# 이슈 목록 가져오기 (히스토리)
@app.get("/api/issues", response_model=List[IssueResponse])
def get_issues(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(Issue).order_by(Issue.created_at.desc()).offset(skip).limit(limit).all()

# 개별 기사 목록 (디버깅용)
@app.get("/api/articles", response_model=List[ArticleResponse])
def get_articles(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    return db.query(Article).order_by(Article.published_at.desc()).offset(skip).limit(limit).all()

# 회원가입 엔드포인트
@app.post("/users", response_model=UserResponse)
def signup(user: UserCreateRequest, db: Session = Depends(get_db)):
    return create_user(db, user.model_dump())

# 사용자 조회 엔드포인트
@app.get("/users/{login_id}", response_model=UserResponse)
def read_user(login_id: str, db: Session = Depends(get_db)):
    return get_user(db, login_id)