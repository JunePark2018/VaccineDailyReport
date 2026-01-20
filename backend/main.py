import threading
import time
from contextlib import asynccontextmanager
from typing import Dict, List, Optional, Any
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_

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

        # 1. 뉴스 수집 (DB 연결)
        db = SessionLocal()
        try:
            # # 스마트 수집 (중복 만나면 중단)
            # # news_list = crawl_breaking_news(limit=20, db_check_session=db)
            # # my_target_media = ["조선", "중앙", "한겨레", "경향", "YTN", "연합", "머니", "매일"]
            # my_target_media = []  # 모든 뉴스 수집. 테스트용
            # news_list = run_article_crawler(my_target_media, days=1, max_pages=5)
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
            #         img_urls=news.get("img_urls"),
            #         created_at=datetime.fromisoformat(news["time"]) if news["time"] != "시간 정보 없음" else None,
            #     ):
            #         count += 1
            #     pass
            # print(f"   -> {count}개의 신규 기사 저장 완료")

            # 군집화 시작
            run_issue_clustering(db, days=3)  # 잘 됨
            pass
        finally:
            db.close()

        # 2. AI 파이프라인 가동 (신규 기사가 있든 없든, 분석 대기 중인 게 있을 수 있으므로 실행)
        process_news_pipeline()

        # 10분(600초) 대기
        print("💤 [Sleep] 10분 대기 중...")
        time.sleep(5)


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


#--------------------------------------------------
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

    Returns:
        keyword (str): 검색 키워드
        definition (dict): 위키피디아 정의 (title, summary, url)
        ai_summaries (list): AI가 요약한 관련 이슈 목록
        hot_topics (list): 이미지가 포함된 실시간 핫토픽 기사 목록
        articles (list): 이미지 여부와 무관한 최신 관련 기사 목록 (Related News용)
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
    skip: int = 0,  # [추가] 앞에서부터 몇 개를 건너뛸지
    limit: int = 10,  # 몇 개를 가져올지
    db: Session = Depends(get_db),
):
    """
    AI가 생성한 뉴스들을 가져옵니다.

    **skip**: 앞에서부터 건너뛸 데이터의 개수 (페이지 번호 구현 시 사용)<br/>
    **limit**: 한 번에 가져올 최대 데이터 개수 (페이지 당 목록 수)<br/>

    """

    # 최신순
    return db.query(AiGeneratedNews).order_by(AiGeneratedNews.created_at.desc()).offset(skip).limit(limit).all()


@app.get("/generated-news/search")
def search_generated_news(
    keyword: str = Query(..., min_length=1, description="검색어"),
    skip: int = 0,  # 앞에서부터 몇 개를 건너뛸지 (0이면 처음부터)
    limit: int = 20,  # 최대 몇 개를 가져올지 (기본값 20개)
    db: Session = Depends(get_db),
):
    """
    AI가 생성한 뉴스에서 '내용(contents)' 또는 '제목(title)'에 키워드가 포함된 뉴스를 찾습니다.

    **keyword**: 검색할 키워드.<br/>
    **skip**: 앞에서부터 건너뛸 데이터의 개수 (페이지 번호 구현 시 사용)<br/>
    **limit**: 한 번에 가져올 최대 데이터 개수 (페이지 당 목록 수)<br/>
    """

    search_pattern = f"%{keyword}%"

    # 1. DB에서 이슈 검색
    results = (
        db.query(AiGeneratedNews)
        .filter(or_(AiGeneratedNews.title.ilike(search_pattern), AiGeneratedNews.contents.ilike(search_pattern)))
        .offset(skip)
        .limit(limit)
        .all()
    )

    # 2. 결과가 있으면 반환 (Cache Hit)
    if results:
        return results

    # 3. 결과가 없으면 빈 리스트 반환
    return []


@app.get("/generated-news/{generated_news_id}")
def get_generated_news_detail(generated_news_id: int, db: Session = Depends(get_db)):
    """
    AI가 생성한 뉴스 중 특정 ID에 해당하는 뉴스를 가져옵니다.

    **generated_news_id**: AI가 생성한 뉴스의 ID.

    """

    # 1. 뉴스를 찾으면서 + 연관된 뉴스도 같이 로딩(joinedload)
    generated_news = (
        db.query(AiGeneratedNews)
        .options(joinedload(AiGeneratedNews.cluster).joinedload(Cluster.news))
        .filter(AiGeneratedNews.id == generated_news_id)
        .first()
    )

    # 2. 없으면 404
    if not generated_news:
        raise HTTPException(status_code=404, detail="해당 뉴스를 찾을 수 없습니다.")

    return generated_news


# 크롤링한 뉴스 목록 (디버깅용)
@app.get("/news", response_model=List[NewsResponse])
def get_news(skip: int = 0, limit: int = 20, region: Optional[str] = None, db: Session = Depends(get_db)):  # [추가]
    """
    크롤링한 뉴스들을 가져옵니다.

    **skip**: 앞에서부터 건너뛸 데이터의 개수 (페이지 번호 구현 시 사용)<br/>
    **limit**: 한 번에 가져올 최대 데이터 개수 (페이지 당 목록 수)<br/>
    **region**: 한정할 지역 ("domestic" or "global")
    """
    query = db.query(News).options(joinedload(News.company))

    if region:
        query = query.filter(News.region == region)

    # 정렬 -> 건너뛰기(skip) -> 자르기(limit) 순서로 실행
    return query.order_by(News.created_at.desc()).offset(skip).limit(limit).all()


@app.get("/news/search", response_model=List[NewsResponse])
def search_news(
    keyword: str = Query(..., min_length=1, description="검색어"),
    region: Optional[str] = None,  # [옵션] 특정 지역 내에서 검색
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    """
    크롤링한 뉴스들에서 '내용(contents)' 또는 '제목(title)'에 키워드가 포함된 뉴스를 찾습니다.

    **keyword**: 제목(title) 또는 본문(contents)에 포함된 단어 검색<br/>
    **region**: (선택) 특정 지역 필터링 ("domestic" or "global")<br/>
    **skip**: 앞에서부터 건너뛸 데이터의 개수 (페이지 번호 구현 시 사용)<br/>
    **limit**: 한 번에 가져올 최대 데이터 개수 (페이지 당 목록 수)<br/>
    """

    # 1. 쿼리 객체 생성
    query = db.query(News)

    # 2. 지역 필터가 있다면 먼저 적용 (범위를 좁혀주므로 성능에 유리)
    if region:
        query = query.filter(News.region == region)

    # 3. 키워드 검색 적용 (제목 OR 본문)
    search_pattern = f"%{keyword}%"
    query = query.filter(or_(News.title.ilike(search_pattern), News.contents.ilike(search_pattern)))

    # 4. 최신순 정렬 + 페이징 적용 후 실행
    results = query.order_by(News.created_at.desc()).offset(skip).limit(limit).all()

    return results


@app.get("/news/{news_id}", response_model=NewsResponse)
def get_news(news_id: int, db: Session = Depends(get_db)):  # URL의 {news_id}가 여기로 들어옵니다.
    """
    크롤링한 뉴스들 중 특정 ID에 해당하는 뉴스를 가져옵니다.

    **id**: 뉴스의 ID.
    """
    # 1. DB에서 ID가 일치하는 뉴스 찾기
    news = db.query(News).filter(News.id == news_id).first()

    # 2. 뉴스가 없으면 404 에러 발생 (매우 중요!)
    if news is None:
        raise HTTPException(status_code=404, detail="뉴스를 찾을 수 없습니다.")

    # 3. 뉴스가 있으면 반환
    return news


# 회원가입 엔드포인트: 중복 아이디 체크 로직 추가
@app.post("/users", response_model=UserResponse)
def signup(user: UserCreateRequest, db: Session = Depends(get_db)):
    """
    새 사용자 정보로 회원가입을 합니다. (중복 아이디 체크 포함)
    """
    # 1. 아이디 중복 체크 (get_user_by_login_id 함수 사용)
    db_user = get_user_by_login_id(db, user.login_id)

    # 2. 이미 존재하면 400 에러 발생
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="이미 존재하는 아이디입니다.")

    # 3. 중복이 아니면 가입 진행
    user_data = user.model_dump(exclude={"subscribed_categories", "subscribed_keywords"})
    new_user = create_user(
        db, **user_data, subscribed_categories=user.subscribed_categories, subscribed_keywords=user.subscribed_keywords
    )

    # 4. 응답 데이터 수동 매핑 (ORM 객체 -> Pydantic 스키마 형변환 이슈 해결)
    # subscribed_categories는 List[Category]이므로 List[str]로 변환 필요
    response_dict = new_user.__dict__.copy()
    response_dict["subscribed_categories"] = [cat.name for cat in new_user.subscribed_categories]
    # kw.keyword는 UserKeywordSubscription 객체의 keyword 필드
    response_dict["subscribed_keywords"] = [kw.keyword for kw in new_user.keyword_subscriptions]

    return response_dict


# 사용자 조회 엔드포인트
@app.get("/users/{login_id}", response_model=UserResponse)
def read_user(login_id: str, db: Session = Depends(get_db)):
    """
    특정 사용자 ID의 정보를 가져옵니다.
    """
    login_id = login_id.strip()  # 앞뒤 공백 제거
    print(f"[DEBUG] 조회 요청된 login_id: '{login_id}'")  # 디버깅용
    user = (
        db.query(User)
        .options(joinedload(User.subscribed_categories), joinedload(User.keyword_subscriptions))
        .filter(User.login_id == login_id)
        .first()
    )
    print(f"[DEBUG] 조회 결과: {user}")  # 디버깅용
    if user is None:
        print(f"[DEBUG] 사용자 '{login_id}'를 찾을 수 없음")  # 디버깅용
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

    # 관계 데이터를 수동으로 매핑
    user_dict = user.__dict__.copy()
    user_dict["subscribed_categories"] = [cat.name for cat in user.subscribed_categories]
    user_dict["subscribed_keywords"] = [kw.keyword for kw in user.keyword_subscriptions]

    return user_dict


# 로그인 엔드포인트
@app.post("/login")
def login(request: UserLoginRequest, db: Session = Depends(get_db)):
    """
    로그인을 합니다. ID나 비밀번호가 맞는지 비교하며, 응답문은 JSON 형태입니다.
    JSON의 success 항목이 True면 로그인에 성공한 것입니다. 자세한 내용은 아래 Schema를 참고해 주세요.
    """

    # 1. 아이디로 유저 찾기
    user = get_user_by_login_id(db, request.login_id)

    # 유저가 없는 경우
    if not user:
        return {"success": False, "message": "존재하지 않는 아이디입니다."}

    # 비밀번호 비교 (DB의 password_hash 컬럼에 저장된 평문과 비교)
    if user.password_hash != request.password:
        return {"success": False, "message": "비밀번호가 틀렸습니다."}

    # 일치하면 성공 메시지 반환
    return {"success": True, "message": "로그인 성공!", "login_id": user.login_id, "user_name": user.user_real_name}


# 사용자 정보 수정
@app.patch("/users/{login_id}")
def update_user_simple(
    login_id: str,  # URL에서 아이디를 받습니다.
    user_update: UserUpdate,  # 수정할 내용을 받습니다.
    db: Session = Depends(get_db),
):
    """
    사용자의 정보를 수정합니다.

    **login_id**: 수정할 사용자의 ID
    """

    # 1. 전달받은 login_id로 DB에서 바로 찾습니다. (인증 X)
    user = db.query(User).filter(User.login_id == login_id).first()
    print(f"[DEBUG] Found user: {user}")  # 디버깅용

    if not user:
        raise HTTPException(status_code=404, detail="해당 아이디의 유저를 찾을 수 없습니다.")

    # 2. 데이터 업데이트 로직
    update_data = user_update.dict(exclude_unset=True)  # 입력된 값만 추출
    print(f"[DEBUG] Update data: {update_data}")  # 디버깅용

    # 관계 필드는 제외하고 업데이트
    excluded_fields = {"subscribed_categories", "subscribed_keywords"}

    for key, value in update_data.items():
        if key in excluded_fields:
            print(f"[DEBUG] Skipping excluded field: {key}")  # 디버깅용
            continue  # 관계 필드는 건너뜀
        elif key == "password":
            # 실제 사용 시에는 여기서 해싱(암호화) 필요
            user.password_hash = value
            print(f"[DEBUG] Updated password_hash")  # 디버깅용
        else:
            setattr(user, key, value)
            print(f"[DEBUG] Updated {key} = {value}")  # 디버깅용

    # 4. 구독 정보 업데이트 (excluded_fields 였던 것들 처리)
    if user_update.subscribed_categories is not None or user_update.subscribed_keywords is not None:
        from database.crud import update_user_subscriptions

        update_user_subscriptions(db, user, user_update.subscribed_categories, user_update.subscribed_keywords)

    # 3. 저장
    try:
        print("[DEBUG] Attempting commit")  # 디버깅용
        db.commit()
        print("[DEBUG] Commit successful")  # 디버깅용
        db.refresh(user)
        print(f"[DEBUG] User refreshed: {user}")  # 디버깅용
    except Exception as e:
        print(f"[DEBUG] Commit failed: {e}")  # 디버깅용
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
    """
    뉴스에 반응 추가.
    """
    user = get_user_by_login_id(db, login_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    from database.crud import set_reaction

    try:
        status, likes, dislikes = set_reaction(db, user_id=user.id, ai_news_id=news_id, value=value)
        db.commit()  # 변경사항 저장
    except ValueError as e:
        db.rollback()
        # 뉴스(AiGeneratedNews)를 찾을 수 없는 경우 등
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")

    return {"message": "Reaction updated", "status": status, "likes": likes, "dislikes": dislikes}


@app.get("/news/{news_id}/reaction")
def get_news_reaction(
    news_id: int, login_id: str = Query(..., description="User Login ID"), db: Session = Depends(get_db)
):
    """
    뉴스의 반응 조회.
    """
    user = get_user_by_login_id(db, login_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    from database.crud import get_reaction

    reaction = get_reaction(db, user_id=user.id, ai_news_id=news_id)
    return {"reaction": reaction}


@app.post("/news/{news_id}/view")
def add_news_view(news_id: int, login_id: str = Query(..., description="User Login ID"), db: Session = Depends(get_db)):
    """
    뉴스 조회 기록 추가.
    """
    user = get_user_by_login_id(db, login_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    from database.crud import add_view

    # crud.add_view(db, user_id, ai_news_id, unique_per_user=True)
    try:
        add_view(db, user_id=user.id, ai_news_id=news_id, unique_per_user=True)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to record view")

    return {"message": "View recorded"}


@app.get("/news/{news_id}/views")
def get_news_views(news_id: int, db: Session = Depends(get_db)):
    """
    뉴스 조회수 조회.
    """
    from database.crud import get_view_count

    count = get_view_count(db, news_id=news_id)
    return {"views": count}


@app.get("/news/{news_id}/reactions")
def get_news_reactions(news_id: int, db: Session = Depends(get_db)):
    """
    뉴스 반응 수 조회.
    """
    from database.crud import get_reaction_counts

    counts = get_reaction_counts(db, news_id=news_id)
    return counts
