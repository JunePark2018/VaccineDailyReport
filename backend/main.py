import threading
import time
from contextlib import asynccontextmanager
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from scraper_en import GlobalNewsScraper

from database.engine import engine, SessionLocal
from database.models import Base, News, AiGeneratedNews, Cluster, User
from schemas import (
    NewsResponse,
    AiGeneratedNewsResponse,
    UserCreateRequest,
    UserLoginRequest,
    UserResponse,
    LogViewRequest,
    UserUpdate,
)
# [수정] scraper.py에서 run_article_crawler 임포트
from scraper import run_article_crawler
from database.crud import create_news, create_user, get_user, get_user_by_login_id, get_or_create_company_by_raw_name
from ai_processor import process_news_pipeline
from clustering import run_issue_clustering
from search_agent import (
    search_wikipedia,
    search_issues_by_keyword,
    search_hot_topics_by_keyword,
    search_articles_by_keyword,
)


# --- [백그라운드 워커] 주기적으로 뉴스 수집 & AI 분석 ---
def run_background_worker():
    print("🚀 [System] 백그라운드 워커 가동 시작")
    
    while True:
        print("\n⏰ [Auto] 뉴스 수집 및 분석 사이클 시작...")
        db = SessionLocal()
        
        try:
            # --- [Step 1] 국내 뉴스 수집 ---
            print("🇰🇷 국내 뉴스 수집 중...")
            target_list = ["조선", "KBS","MBC","SBS","연합","한겨레","중앙","경향","한국","JTBC"]
            # target_list = [] # 테스트용 빈 리스트
            
            # [연동] 수정된 scraper.py의 함수 호출 (db 세션 전달)
            news_list = run_article_crawler(db, target_companies=target_list)
            
            for news in news_list:
                company = get_or_create_company_by_raw_name(db, news["company_name"])
                create_news(
                    db,
                    title=news["title"],
                    contents=news["contents"],
                    url=news["url"],
                    company_id=company.id,
                    region="domestic",
                    # [추가] 수집된 카테고리 정보를 DB에 저장 (중요!)
                    category=news.get("category"), 
                    img_urls=news.get("img_urls"),
                    created_at=datetime.fromisoformat(news["time"]) if news["time"] != "시간 정보 없음" else datetime.now()
                )
            db.commit()

            # --- [Step 2] 군집화 및 AI 분석 (요약 + 영문 키워드 생성) ---
            print("🤖 군집화 및 AI 이슈 분석 중...")
            run_issue_clustering(db, days=3)
            
            # 이 단계에서 AiGeneratedNews 테이블에 search_keyword와 함께 저장되어야 함
            process_news_pipeline() 
            db.commit()

            # --- [Step 3] 지연된 외신 추적  ---
            if GlobalNewsScraper:
                # 상태가 PENDING이고 생성된 지 24시간 이내인 이슈들만 추적
                BATCH_SIZE = 10

                pending_issues = db.query(AiGeneratedNews).filter(
                    AiGeneratedNews.global_search_status == "PENDING",
                    AiGeneratedNews.created_at >= datetime.now() - timedelta(hours=24)
                ).order_by(AiGeneratedNews.search_retry_count.asc()) \
                 .limit(BATCH_SIZE) \
                 .all()

                if pending_issues:
                    print(f"🌍 [Batch] 대기 중인 이슈 {len(pending_issues)}개 외신 추적 시작 (Limit: {BATCH_SIZE})...")
                    en_scraper = GlobalNewsScraper()
                    
                    for issue in pending_issues:
                        # 1. 24시간 초과 체크 (DB 쿼리 필터와 별개로 안전장치)
                        time_diff = datetime.now() - issue.created_at
                        if time_diff > timedelta(hours=24):
                             issue.global_search_status = "FAILED"
                             print(f"💀 '{issue.title}' 시간 초과로 추적 종료")
                             continue
                        
                        if not issue.search_keyword:
                            continue
                            
                        print(f"🔍 [Retry {issue.search_retry_count}] 키워드: '{issue.search_keyword}'")
                        
                        # 스크래핑 수행
                        en_results = en_scraper.run(issue.search_keyword)

                        if en_results:
                            # 성공 로직
                            for en_data in en_results:
                                company = get_or_create_company_by_raw_name(db, en_data["company_name"])
                                create_news(
                                    db,
                                    title=en_data["title"],
                                    contents=en_data["contents"],
                                    url=en_data["url"],
                                    company_id=company.id,
                                    region="global",
                                    category=en_data.get("category"), # 카테고리 추가
                                    img_urls=en_data.get("img_urls"),
                                    created_at=datetime.now()
                                )
                            issue.global_search_status = "SUCCESS"
                            print(f"✨ '{issue.title}' 외신 발견 성공!")
                        else:
                            # 실패 시: 카운트만 증가시키고 상태는 PENDING 유지
                            issue.search_retry_count += 1
                            print(f"💨 '{issue.title}' 외신 없음. (Retry: {issue.search_retry_count})")
                    
                    en_scraper.close() # 브라우저 종료
                    db.commit()

        except Exception as e:
            print(f"❌ [Error] 백그라운드 워커 오류: {e}")
            db.rollback()
        finally:
            db.close()

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

# --------------------------------------------------
#             프론트-백 FastAPI 연결
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --------------------------------------------------


# DB 세션 의존성
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- [API 엔드포인트] ---


# 통합 검색 엔드포인트
@app.get("/api/comprehensive-search")
def comprehensive_search(keyword: str = Query(..., min_length=1, description="검색어"), db: Session = Depends(get_db)):
    """
    통합 검색 API: 위키피디아, AI 요약, 핫토픽, 관련 기사를 한 번에 반환합니다.
    """
    # 1. 위키피디아 검색 (외부 API)
    wiki_info = search_wikipedia(keyword)

    # 2. AI 이슈 요약 검색 (DB: Issue)
    ai_summaries = search_issues_by_keyword(db, keyword)

    # 3. 핫토픽 검색 (DB: Article, 이미지 포함 & 조회수/최신순)
    hot_topics = search_hot_topics_by_keyword(db, keyword)

    # 4. 관련 기사 검색 (DB: Article, 최신순)
    articles = search_articles_by_keyword(db, keyword)

    return {
        "keyword": keyword,
        "definition": wiki_info,
        "ai_summaries": ai_summaries,
        "hot_topics": hot_topics,
        "articles": articles,
    }


# AI 생성 뉴스 목록 가져오기 (히스토리)
@app.get("/generated-news", response_model=List[AiGeneratedNewsResponse])
def get_generated_news(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    return db.query(AiGeneratedNews).order_by(AiGeneratedNews.created_at.desc()).offset(skip).limit(limit).all()


@app.get("/generated-news/search")
def search_generated_news(
    keyword: str = Query(..., min_length=1, description="검색어"),
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    search_pattern = f"%{keyword}%"
    results = (
        db.query(AiGeneratedNews)
        .filter(or_(AiGeneratedNews.title.ilike(search_pattern), AiGeneratedNews.contents.ilike(search_pattern)))
        .offset(skip)
        .limit(limit)
        .all()
    )
    if results:
        return results
    return []


@app.get("/generated-news/{generated_news_id}")
def get_generated_news_detail(generated_news_id: int, db: Session = Depends(get_db)):
    generated_news = (
        db.query(AiGeneratedNews)
        .options(joinedload(AiGeneratedNews.cluster).joinedload(Cluster.news))
        .filter(AiGeneratedNews.id == generated_news_id)
        .first()
    )
    if not generated_news:
        raise HTTPException(status_code=404, detail="해당 뉴스를 찾을 수 없습니다.")
    return generated_news


# 크롤링한 뉴스 목록
@app.get("/news", response_model=List[NewsResponse])
def get_news(skip: int = 0, limit: int = 20, region: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(News).options(joinedload(News.company))
    if region:
        query = query.filter(News.region == region)
    return query.order_by(News.created_at.desc()).offset(skip).limit(limit).all()


@app.get("/news/search", response_model=List[NewsResponse])
def search_news(
    keyword: str = Query(..., min_length=1, description="검색어"),
    region: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    query = db.query(News)
    if region:
        query = query.filter(News.region == region)
    
    search_pattern = f"%{keyword}%"
    query = query.filter(or_(News.title.ilike(search_pattern), News.contents.ilike(search_pattern)))
    
    return query.order_by(News.created_at.desc()).offset(skip).limit(limit).all()


@app.get("/news/{news_id}", response_model=NewsResponse)
def get_news(news_id: int, db: Session = Depends(get_db)):
    news = db.query(News).filter(News.id == news_id).first()
    if news is None:
        raise HTTPException(status_code=404, detail="뉴스를 찾을 수 없습니다.")
    return news


# 회원가입 엔드포인트
@app.post("/users", response_model=UserResponse)
def signup(user: UserCreateRequest, db: Session = Depends(get_db)):
    db_user = get_user_by_login_id(db, user.login_id)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="이미 존재하는 아이디입니다.")

    user_data = user.model_dump(exclude={"subscribed_categories", "subscribed_keywords"})
    new_user = create_user(
        db, **user_data, subscribed_categories=user.subscribed_categories, subscribed_keywords=user.subscribed_keywords
    )

    response_dict = new_user.__dict__.copy()
    response_dict["subscribed_categories"] = [cat.name for cat in new_user.subscribed_categories]
    response_dict["subscribed_keywords"] = [kw.keyword for kw in new_user.keyword_subscriptions]
    return response_dict


# 사용자 조회 엔드포인트
@app.get("/users/{login_id}", response_model=UserResponse)
def read_user(login_id: str, db: Session = Depends(get_db)):
    login_id = login_id.strip()
    user = (
        db.query(User)
        .options(joinedload(User.subscribed_categories), joinedload(User.keyword_subscriptions))
        .filter(User.login_id == login_id)
        .first()
    )
    if user is None:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

    user_dict = user.__dict__.copy()
    user_dict["subscribed_categories"] = [cat.name for cat in user.subscribed_categories]
    user_dict["subscribed_keywords"] = [kw.keyword for kw in user.keyword_subscriptions]
    return user_dict


# 로그인 엔드포인트
@app.post("/login")
def login(request: UserLoginRequest, db: Session = Depends(get_db)):
    user = get_user_by_login_id(db, request.login_id)
    if not user:
        return {"success": False, "message": "존재하지 않는 아이디입니다."}
    if user.password_hash != request.password:
        return {"success": False, "message": "비밀번호가 틀렸습니다."}
    return {"success": True, "message": "로그인 성공!", "login_id": user.login_id, "user_name": user.user_real_name}


# 사용자 정보 수정
@app.patch("/users/{login_id}")
def update_user_simple(
    login_id: str,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.login_id == login_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="해당 아이디의 유저를 찾을 수 없습니다.")

    update_data = user_update.dict(exclude_unset=True)
    excluded_fields = {"subscribed_categories", "subscribed_keywords"}

    for key, value in update_data.items():
        if key in excluded_fields:
            continue
        elif key == "password":
            user.password_hash = value
        else:
            setattr(user, key, value)

    if user_update.subscribed_categories is not None or user_update.subscribed_keywords is not None:
        from database.crud import update_user_subscriptions
        update_user_subscriptions(db, user, user_update.subscribed_categories, user_update.subscribed_keywords)

    try:
        db.commit()
        db.refresh(user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="DB 업데이트 실패")

    return {"message": f"'{login_id}'님의 정보가 수정되었습니다."}


# 뉴스 반응 관련 엔드포인트
@app.post("/news/{news_id}/reaction")
def add_news_reaction(
    news_id: int,
    value: int = Query(..., description="1 for like, -1 for dislike"),
    login_id: str = Query(..., description="User Login ID"),
    db: Session = Depends(get_db),
):
    user = get_user_by_login_id(db, login_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    from database.crud import set_reaction
    try:
        status, likes, dislikes = set_reaction(db, user_id=user.id, ai_news_id=news_id, value=value)
        db.commit()
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")

    return {"message": "Reaction updated", "status": status, "likes": likes, "dislikes": dislikes}


@app.get("/news/{news_id}/reaction")
def get_news_reaction(
    news_id: int, login_id: str = Query(..., description="User Login ID"), db: Session = Depends(get_db)
):
    user = get_user_by_login_id(db, login_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    from database.crud import get_reaction
    reaction = get_reaction(db, user_id=user.id, ai_news_id=news_id)
    return {"reaction": reaction}


@app.post("/news/{news_id}/view")
def add_news_view(news_id: int, login_id: str = Query(..., description="User Login ID"), db: Session = Depends(get_db)):
    user = get_user_by_login_id(db, login_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    from database.crud import add_view
    try:
        add_view(db, user_id=user.id, ai_news_id=news_id, unique_per_user=True)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to record view")
    return {"message": "View recorded"}


@app.get("/news/{news_id}/views")
def get_news_views(news_id: int, db: Session = Depends(get_db)):
    from database.crud import get_view_count
    count = get_view_count(db, news_id=news_id)
    return {"views": count}


@app.get("/news/{news_id}/reactions")
def get_news_reactions(news_id: int, db: Session = Depends(get_db)):
    from database.crud import get_reaction_counts
    counts = get_reaction_counts(db, news_id=news_id)
    return counts