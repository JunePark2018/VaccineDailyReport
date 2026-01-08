import threading
import time
from contextlib import asynccontextmanager
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from database import engine, SessionLocal
from models import Base, Article, Issue, User
from schemas import ArticleResponse, IssueResponse, UserCreateRequest, UserResponse, LogViewRequest, UserUpdate
from scraper import run_article_crawler
from crud import create_article, create_user, get_user, increase_user_interest
from ai_processor import process_news_pipeline 

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
@app.get("/issues", response_model=List[IssueResponse])
def get_issues(limit: int = 10, db: Session = Depends(get_db)):
    return db.query(Issue).order_by(Issue.created_at.desc()).limit(limit).all()

# 개별 기사 목록 (디버깅용)
@app.get("/articles", response_model=List[ArticleResponse])
def get_articles(
    limit: int = 20, 
    category: Optional[str] = None, # [추가] 카테고리 입력을 선택적으로 받음
    db: Session = Depends(get_db)
):
    # 1. 일단 모든 기사를 가져올 준비를 합니다.
    query = db.query(Article)
    
    # 2. 만약 URL에 category가 들어왔다면? (예: ?category=IT)
    if category:
        # DB에서 해당 카테고리만 필터링합니다.
        query = query.filter(Article.category == category)
        
    # 3. 최신순 정렬 후 limit만큼 잘라서 반환
    return query.order_by(Article.time.desc()).limit(limit).all()

# 회원가입 엔드포인트
@app.post("/users", response_model=UserResponse)
def signup(user: UserCreateRequest, db: Session = Depends(get_db)):
    return create_user(db, user.model_dump())

# 사용자 조회 엔드포인트
@app.get("/users/{login_id}", response_model=UserResponse)
def read_user(login_id: str, db: Session = Depends(get_db)):
    return get_user(db, login_id)

# 사용자가 기사를 클릭했을때 호출. 카테고리, 키워드 횟수 증가
@app.post("/increase_user_interest")
def log_article_view(request: LogViewRequest, db: Session = Depends(get_db)):
    updated_user = increase_user_interest(
        db=db,
        user_id=request.login_id,
        category=request.category,
        keyword=request.keyword
    )
    
    if not updated_user:
        return {"message": "User not found", "success": False}
        
    return {"message": "Interest updated", "success": True}

# 사용자 정보 수정
@app.patch("/users/{login_id}")
def update_user_simple(
    login_id: str,               # URL에서 아이디를 받습니다.
    user_update: UserUpdate,     # 수정할 내용을 받습니다.
    db: Session = Depends(get_db)
):
    # 1. 전달받은 login_id로 DB에서 바로 찾습니다. (인증 X)
    user = db.query(User).filter(User.login_id == login_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="해당 아이디의 유저를 찾을 수 없습니다.")

    # 2. 데이터 업데이트 로직
    update_data = user_update.dict(exclude_unset=True) # 입력된 값만 추출

    for key, value in update_data.items():
        if key == "password":
            # 실제 사용 시에는 여기서 해싱(암호화) 필요
            user.password_hash = value  
        else:
            setattr(user, key, value)

    # 3. 저장
    try:
        db.commit()
        db.refresh(user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="DB 업데이트 실패")

    return {"message": f"'{login_id}'님의 정보가 수정되었습니다."}

# 로그인 엔드포인트
@app.post("/login")
def login(request: UserLoginRequest, db: Session = Depends(get_db)):
    # 1. 아이디로 유저 찾기
    user = get_user(db, request.login_id)

# 유저가 없는 경우
    if not user:
        return {"success": False, "message": "존재하지 않는 아이디입니다."}

# 비밀번호 비교 (DB의 password_hash 컬럼에 저장된 평문과 비교)
    if user.password_hash != request.password:
        return {"success": False, "message": "비밀번호가 틀렸습니다."}

# 일치하면 성공 메시지 반환
    return {
        "success": True, 
        "message": "로그인 성공!",
        "login_id": user.login_id,
        "user_name": user.user_real_name
    }
