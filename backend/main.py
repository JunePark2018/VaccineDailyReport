import threading
import time
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.engine import engine, SessionLocal
from database.models import Base
from scraper import crawl_n_days
from database.crud import create_news, get_or_create_company_by_raw_name
from ai_processor import process_news_pipeline
from clustering import run_issue_clustering


# --- [백그라운드 워커] 주기적으로 뉴스 수집 & AI 분석 ---
def run_background_worker():
    print("🚀 [System] 백그라운드 워커 가동 시작")
    while True:
        print("\n⏰ [Auto] 뉴스 수집 및 분석 사이클 시작...")

        # 1. 뉴스 수집 (DB 연결)
        db = SessionLocal()
        try:
            # # 스마트 수집 (중복 만나면 중단)
            # # news_list = crawl_breaking_news(limit=20, db_check_session=db)
            # # my_target_media = ["조선", "중앙", "한겨레", "경향", "YTN", "연합", "머니", "매일"]
            # my_target_media = []  # 모든 뉴스 수집. 테스트용
            # # news_list = run_article_crawler(my_target_media) # 속보 긁어오기
            # news_list = crawl_n_days(sections=("100",), n_days=1, pages_per_day=20)  # 최근 n일치 뉴스 긁어오기
            # count = 0
            # for news in news_list:
            #     # 기사 db에 저장
            #     company = get_or_create_company_by_raw_name(db, news["company_name"])
            #     if create_news(
            #         db,
            #         title=news["title"],
            #         contents=news["contents"],
            #         url=news["url"],
            #         company_id=company.id,
            #         region="domestic",  # 기본값
            #         category=news.get("category"),  # scraper에서 가져온 카테고리
            #         img_urls=news.get("img_urls"),
            #         created_at=datetime.fromisoformat(news["time"]) if news["time"] != "시간 정보 없음" else None,
            #     ):
            #         count += 1
            #     pass
            # print(f"   -> {count}개의 신규 기사 저장 완료")
            # db.commit()  # DB 커밋

            run_issue_clustering(db, days=3)  # 군집화
        finally:
            db.close()

        # 2. AI 파이프라인 가동
        process_news_pipeline()

        print("💤 [Sleep] 10분 대기 중...")
        time.sleep(600)


# --- [FastAPI 앱 설정] ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    worker_thread = threading.Thread(target=run_background_worker, daemon=True)
    worker_thread.start()
    yield
    print("👋 서버 종료")


app = FastAPI(lifespan=lifespan)


# CORS 설정
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


# 라우터 등록
from routers import ai_news, news, users, auth, statistics, categories, search_logs, reactions, search

app.include_router(ai_news.router)
app.include_router(news.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(statistics.router)
app.include_router(categories.router)
app.include_router(search_logs.router)
app.include_router(reactions.router)
app.include_router(search.router)


# DB 세션 의존성 (legacy support)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
