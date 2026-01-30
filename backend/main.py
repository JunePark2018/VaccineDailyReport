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

        # try:
        #     # --- [Step 1] 국내 뉴스 수집 ---
        #     print("🇰🇷 국내 뉴스 수집 중...")
        #     target_list = ["조선", "KBS", "MBC", "SBS", "연합", "한겨레", "중앙", "경향", "한국", "JTBC"]
        #     # target_list = []  # 테스트용 빈 리스트

        #     # [연동] 수정된 scraper.py의 함수 호출 (db 세션 전달)
        #     news_list = run_article_crawler(db, target_companies=target_list)

        #     for news in news_list:
        #         company = get_or_create_company_by_raw_name(db, news["company_name"])
        #         create_news(
        #             db,
        #             title=news["title"],
        #             contents=news["contents"],
        #             url=news["url"],
        #             company_id=company.company_id,
        #             is_domestic=True,
        #             # [추가] 수집된 카테고리 정보를 DB에 저장 (중요!)
        #             category=news.get("category"),
        #             img_urls=news.get("img_urls"),
        #             created_at=(
        #                 datetime.fromisoformat(news["time"]) if news["time"] != "시간 정보 없음" else datetime.now()
        #             ),
        #         )
        #     db.commit()

        #     # --- [Step 2] 군집화 및 AI 분석 (요약 + 영문 키워드 생성) ---
        #     print("🤖 군집화 및 AI 이슈 분석 중...")
        #     run_issue_clustering(db, days=3)

        #     # 이 단계에서 AiGeneratedNews 테이블에 search_keyword와 함께 저장되어야 함
        #     process_news_pipeline()
        #     db.commit()

        #     # --- [Step 3] 지연된 외신 추적  ---
        #     if GlobalNewsScraper:
        #         # 상태가 PENDING이고 생성된 지 24시간 이내인 이슈들만 추적
        #         BATCH_SIZE = 10

        #         pending_issues = (
        #             db.query(AiGeneratedNews)
        #             .filter(
        #                 AiGeneratedNews.global_search_status == "PENDING",
        #                 AiGeneratedNews.created_at >= datetime.now() - timedelta(hours=24),
        #             )
        #             .order_by(AiGeneratedNews.search_retry_count.asc())
        #             .limit(BATCH_SIZE)
        #             .all()
        #         )

        #         if pending_issues:
        #             print(f"🌍 [Batch] 대기 중인 이슈 {len(pending_issues)}개 외신 추적 시작 (Limit: {BATCH_SIZE})...")
        #             en_scraper = GlobalNewsScraper()

        #             for issue in pending_issues:
        #                 # 1. 24시간 초과 체크 (DB 쿼리 필터와 별개로 안전장치)
        #                 time_diff = datetime.now() - issue.created_at
        #                 if time_diff > timedelta(hours=24):
        #                     issue.global_search_status = "FAILED"
        #                     print(f"💀 '{issue.title}' 시간 초과로 추적 종료")
        #                     continue

        #                 if not issue.search_keyword:
        #                     continue

        #                 print(f"🔍 [Retry {issue.search_retry_count}] 키워드: '{issue.search_keyword}'")

        #                 # 스크래핑 수행
        #                 en_results = en_scraper.run(issue.search_keyword)

        #                 if en_results:
        #                     # 성공 로직
        #                     for en_data in en_results:
        #                         company = get_or_create_company_by_raw_name(db, en_data["company_name"])
        #                         create_news(
        #                             db,
        #                             title=en_data["title"],
        #                             contents=en_data["contents"],
        #                             url=en_data["url"],
        #                             company_id=company.company_id,
        #                             is_domestic=False,
        #                             category=en_data.get("category"),  # 카테고리 추가
        #                             img_urls=en_data.get("img_urls"),
        #                             created_at=datetime.now(),
        #                         )
        #                     issue.global_search_status = "SUCCESS"
        #                     print(f"✨ '{issue.title}' 외신 발견 성공!")
        #                 else:
        #                     # 실패 시: 카운트만 증가시키고 상태는 PENDING 유지
        #                     issue.search_retry_count += 1
        #                     print(f"💨 '{issue.title}' 외신 없음. (Retry: {issue.search_retry_count})")

        #             en_scraper.close()  # 브라우저 종료
        #             db.commit()

        # except Exception as e:
        #     print(f"❌ [Error] 백그라운드 워커 오류: {e}")
        #     db.rollback()
        # finally:
        #     db.close()

        print("💤 [Sleep] 1분 대기 중...")
        time.sleep(60)


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

#서버목록
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://168.107.51.224:3000/",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

