# crud.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, List, Optional, Sequence, Tuple, Dict

from sqlalchemy import and_, delete, func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .models import (
    Company,
    Cluster,
    News,
    AiGeneratedNews,
    User,
    Category,
    NewsReaction,
    NewsView,
    SearchLog,
    UserKeywordReadStat,
    UserKeywordSubscription,
    cluster_news_link,
)


# -------------------------
# 작은 유틸
# -------------------------
def normalize_keyword(s: str) -> str:
    # 최소 정규화: 앞뒤 공백 제거 + 내부 연속 공백 1개로
    s = (s or "").strip()
    s = " ".join(s.split())
    return s


# -------------------------
# Company / Alias
# -------------------------
def get_company_by_id(db: Session, company_id: int) -> Optional[Company]:
    return db.get(Company, company_id)


def get_company_by_name(db: Session, name: str) -> Optional[Company]:
    name = (name or "").strip()
    return db.execute(select(Company).where(Company.name == name)).scalar_one_or_none()


def get_or_create_company_by_raw_name(
    db: Session,
    raw_company_name: str,
    display_name: Optional[str] = None,
) -> Company:
    """
    크롤러가 준 raw_company_name으로:
    1) Company.name으로 찾기
    2) 없으면 새로 생성
    """
    raw = (raw_company_name or "").strip()
    if not raw:
        raise ValueError("raw_company_name is empty")

    # 1) Company.name으로 찾기
    company = get_company_by_name(db, raw)
    if company:
        return company

    # 2) 새로 만들기
    company = Company(name=raw, display_name=display_name)
    db.add(company)
    db.flush()  # company.company_id 확보
    return company


# -------------------------
# News
# -------------------------
def create_news(
    db: Session,
    *,
    title: Optional[str],
    contents: Optional[str],
    url: str,
    company_id: int,
    is_domestic: bool = True,
    category: Optional[str] = None,  # 정치, 경제, 사회, 생활/문화, 세계, IT/과학
    img_urls: Optional[dict | list] = None,
    created_at: Optional[datetime] = None,
) -> Optional[News]:
    # Check if news with this URL already exists
    existing = get_news_by_url(db, url)
    if existing:
        return None  # Already exists, don't create

    # Category 처리: 문자열을 받아서 Category 테이블에서 찾거나 생성
    category_id = None
    if category:
        category_name = category.strip()
        cat = db.execute(select(Category).where(Category.name == category_name)).scalar_one_or_none()
        if not cat:
            cat = Category(name=category_name)
            db.add(cat)
            db.flush()
        category_id = cat.category_id

    obj = News(
        title=title,
        contents=contents,
        url=url,
        company_id=company_id,
        is_domestic=is_domestic,
        category_id=category_id,
        img_urls=img_urls,
        created_at=created_at or datetime.utcnow(),
    )
    db.add(obj)
    db.flush()
    return obj


def get_news_statistics(db: Session) -> dict:
    """
    News 통계 반환: 전체 개수 + 카테고리별 개수
    Returns:
        {
            "total": 100,
            "by_category": {
                "정치": 20,
                "경제": 30,
                ...
            }
        }
    """
    from sqlalchemy import func

    # 전체 개수
    total = db.query(func.count(News.news_id)).scalar()

    # 카테고리별 개수 (category_id, count)
    category_counts = db.query(News.category_id, func.count(News.news_id)).group_by(News.category_id).all()

    # category_id를 category name으로 변환
    by_category = {}
    for cat_id, count in category_counts:
        if cat_id:
            cat_name = get_category_name(db, cat_id)
            by_category[cat_name or f"ID:{cat_id}"] = count
        else:
            by_category["미분류"] = count

    return {"total": total, "by_category": by_category}


def get_news_by_url(db: Session, url: str) -> Optional[News]:
    return db.execute(select(News).where(News.url == url)).scalar_one_or_none()


def get_news(db: Session, news_id: int) -> Optional[News]:
    return db.get(News, news_id)


def get_recent_news(db: Session, since: datetime) -> List[News]:
    return db.query(News).filter(News.created_at >= since).all()


# -------------------------
# Cluster
# -------------------------
def create_cluster(db: Session, *, title: str) -> Cluster:
    obj = Cluster(title=title)
    db.add(obj)
    db.flush()
    return obj


def get_cluster(db: Session, cluster_id: int) -> Optional[Cluster]:
    return db.get(Cluster, cluster_id)


def add_news_to_cluster(db: Session, *, cluster_id: int, news_id: int) -> None:
    """
    M:N 연결 테이블(cluster_news_link)에 (cluster_id, news_id) 추가.
    """
    # 이미 있으면 아무 것도 안 함(중복 시 IntegrityError 회피)
    exists = db.execute(
        select(cluster_news_link.c.cluster_id).where(
            and_(
                cluster_news_link.c.cluster_id == cluster_id,
                cluster_news_link.c.news_id == news_id,
            )
        )
    ).first()
    if exists:
        return

    db.execute(cluster_news_link.insert().values(cluster_id=cluster_id, news_id=news_id))


def remove_news_from_cluster(db: Session, *, cluster_id: int, news_id: int) -> int:
    """
    삭제된 row 수 반환
    """
    res = db.execute(
        delete(cluster_news_link).where(
            and_(
                cluster_news_link.c.cluster_id == cluster_id,
                cluster_news_link.c.news_id == news_id,
            )
        )
    )
    return res.rowcount or 0


def get_original_news_details_by_cluster(db: Session, cluster_id: int) -> List[dict]:
    """
    cluster_id를 받아서 연결된 원본 기사들의 [제목, URL, 언론사명]을 반환합니다.
    (Sources 컴포넌트용 데이터)
    """
    # 1. News, Company, cluster_news_link 3개를 조인(Join)합니다.
    results = (
        db.query(
            News.news_id,
            News.title,
            News.url,
            Company.name.label("company_name"),
            News.img_urls,
            News.contents,
            News.created_at,
        )
        .join(cluster_news_link, News.news_id == cluster_news_link.c.news_id)
        .join(Company, News.company_id == Company.company_id)
        .filter(cluster_news_link.c.cluster_id == cluster_id)
        .all()
    )

    # 2. 프론트엔드가 쓰기 편한 리스트 형태로 변환
    return [
        {
            "news_id": row.news_id,
            "title": row.title,
            "company_name": row.company_name,
            "url": row.url,
            "img_urls": row.img_urls,
            "contents": row.contents,
            "created_at": row.created_at,
        }
        for row in results
    ]


# -------------------------
# AiGeneratedNews
# -------------------------
def create_ai_generated_news(
    db: Session,
    *,
    cluster_id: int,
    title: Optional[str],
    contents: Optional[str],
    keywords: Optional[list],
    analysis_result: Optional[dict],
    category_id: Optional[int] = None,
    created_at: Optional[datetime] = None,
) -> AiGeneratedNews:
    obj = AiGeneratedNews(
        cluster_id=cluster_id,
        category_id=category_id,
        title=title,
        contents=contents,
        keywords=keywords,
        analysis_result=analysis_result,
        created_at=created_at or datetime.utcnow(),
        like_count=0,
        dislike_count=0,
    )
    db.add(obj)
    db.flush()
    return obj


def get_ai_generated_news(db: Session, ai_news_id: int) -> Optional[AiGeneratedNews]:
    return db.get(AiGeneratedNews, ai_news_id)


def list_ai_generated_news_by_cluster(db: Session, cluster_id: int, limit: int = 50) -> List[AiGeneratedNews]:
    return list(
        db.execute(
            select(AiGeneratedNews)
            .where(AiGeneratedNews.cluster_id == cluster_id)
            .order_by(AiGeneratedNews.created_at.desc())
            .limit(limit)
        ).scalars()
    )


def list_ai_generated_news_by_category(db: Session, category_id: int, limit: int = 50) -> List[AiGeneratedNews]:
    """
    특정 카테고리의 AI 생성 뉴스 목록 조회.
    """
    return list(
        db.execute(
            select(AiGeneratedNews)
            .where(AiGeneratedNews.category_id == category_id)
            .order_by(AiGeneratedNews.created_at.desc())
            .limit(limit)
        ).scalars()
    )


def create_ai_news_issue(
    db: Session, *, title: str, article_ids: List[int], category_id: Optional[int] = None
) -> AiGeneratedNews:
    """
    clustering.py에서 사용하는 이슈 생성 함수.
    Cluster를 생성하고, AiGeneratedNews와 News를 연결합니다.
    """
    # 1. Cluster 생성
    cluster = Cluster(title=title)
    db.add(cluster)
    db.flush()  # cluster.cluster_id 확보

    # 2. AiGeneratedNews 생성
    issue = AiGeneratedNews(
        cluster_id=cluster.cluster_id, category_id=category_id, title=title, created_at=datetime.utcnow()
    )
    db.add(issue)
    db.flush()

    # 3. 기사 연결 (M:N 관계 테이블에 추가)
    if article_ids:
        # bulk insert for M:N
        # 이미 존재하는지 체크하지 않고 넣으면 중복 에러 가능성 있음
        # 하지만 새로 만든 클러스터라 비어있음이 보장됨.
        vals = [{"cluster_id": cluster.cluster_id, "news_id": nid} for nid in article_ids]
        db.execute(cluster_news_link.insert(), vals)
        db.flush()

    return issue


# -------------------------
# User
# -------------------------
def create_user(
    db: Session,
    *,
    login_id: str,
    password_hash: str,
    user_real_name: Optional[str] = None,
    email: Optional[str] = None,
    age_range: Optional[str] = None,
    gender: Optional[str] = None,
    fcm_token: Optional[str] = None,
    marketing_agree: bool = False,
    user_status: int = 1,
    subscribed_categories: Optional[List[str]] = None,
    subscribed_keywords: Optional[List[str]] = None,
) -> User:
    obj = User(
        login_id=login_id,
        password_hash=password_hash,
        user_real_name=user_real_name,
        email=email,
        age_range=age_range,
        gender=gender,
        fcm_token=fcm_token,
        marketing_agree=marketing_agree,
        user_status=user_status,
        created_at=datetime.utcnow(),
    )
    db.add(obj)
    db.commit()  # To get obj.user_id

    # Handle Subscriptions
    if subscribed_categories:
        for cat_name in subscribed_categories:
            cat_name = cat_name.strip()
            if not cat_name:
                continue

            # Check if category exists, if not create it
            cat = db.execute(select(Category).where(Category.name == cat_name)).scalar_one_or_none()
            if not cat:
                cat = Category(name=cat_name)
                db.add(cat)
                db.flush()  # Ensure ID is generated and name persistence

            # Now append to user subscriptions
            # Avoid duplicates if user sends same category twice
            if cat not in obj.subscribed_categories:
                obj.subscribed_categories.append(cat)

    if subscribed_keywords:
        for keyword in subscribed_keywords:
            # Check for existing subscription to avoid duplicates handled by unique constraint or add logic
            # Since it's a new user, we can just add.
            # But safer to use the helper or just add manually.
            # Using normalize_keyword helper if available or just strip.
            # crud.py has normalize_keyword at top.
            normalized_kw = normalize_keyword(keyword)
            if normalized_kw:
                obj.keyword_subscriptions.append(UserKeywordSubscription(keyword=normalized_kw))

    if subscribed_categories or subscribed_keywords:
        db.commit()

    db.refresh(obj)  # 최신 상태로 갱신
    return obj


def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.get(User, user_id)


def get_user_by_login_id(db: Session, login_id: str) -> Optional[User]:
    print(f"[DEBUG] get_user_by_login_id called with login_id: '{login_id}'")  # 디버깅용
    result = db.execute(select(User).where(User.login_id == login_id)).scalar_one_or_none()
    print(f"[DEBUG] Query result: {result}")  # 디버깅용
    return result


def update_user_subscriptions(
    db: Session, user: User, new_categories: Optional[List[str]], new_keywords: Optional[List[str]]
) -> None:
    """
    사용자의 구독 정보(카테고리, 키워드)를 완전히 교체(Replace)합니다.
    None이 들어오면 해당 항목은 건드리지 않고, 빈 리스트([])가 들어오면 모두 삭제합니다.
    """
    # 1. Categories
    if new_categories is not None:
        # 기존 구독 모두 해제 (관계만 끊김)
        user.subscribed_categories.clear()

        for cat_name in new_categories:
            cat_name = cat_name.strip()
            if not cat_name:
                continue

            # Find or Create
            cat = db.execute(select(Category).where(Category.name == cat_name)).scalar_one_or_none()
            if not cat:
                cat = Category(name=cat_name)
                db.add(cat)
                db.flush()

            if cat not in user.subscribed_categories:
                user.subscribed_categories.append(cat)

    # 2. Keywords
    if new_keywords is not None:
        # 기존 키워드 구독 날리기 (delete-orphan cascade 동작 기대)
        # user.keyword_subscriptions is a relationship list.
        # Clearing it should trigger deletion if cascade="all, delete-orphan" is set.
        # User defined: keyword_subscriptions = relationship(..., cascade="all, delete-orphan", ...)
        user.keyword_subscriptions.clear()

        for k in new_keywords:
            normalized_kw = normalize_keyword(k)
            if not normalized_kw:
                continue

            # Add new subscription
            # 주의: (user_id, keyword) PK이므로 중복 없는지 체크 필요?
            # clear() 했으므로 중복은 입력 리스트 내 중복만 체크하면 됨.

            # We can't easily check against `user.keyword_subscriptions` because it's pending flush/clear.
            # actually `clear()` removes them from session.
            pass

        # Deduplicate and add
        unique_kws = set()
        for k in new_keywords:
            n = normalize_keyword(k)
            if n:
                unique_kws.add(n)

        for kw in unique_kws:
            user.keyword_subscriptions.append(UserKeywordSubscription(keyword=kw))

    db.flush()


# -------------------------
# Search log
# -------------------------
def add_search_log(db: Session, *, user_id: int, query: str) -> SearchLog:
    obj = SearchLog(user_id=user_id, query=query, searched_at=datetime.utcnow())
    db.add(obj)
    db.flush()
    return obj


# -------------------------
# Views (AiGeneratedNews 기준)
# -------------------------
def add_view(
    db: Session,
    *,
    user_id: int,
    ai_news_id: int,
    unique_per_user: bool = True,
) -> None:
    """
    unique_per_user=True: (user_id, ai_news_id) 이미 있으면 업데이트만(또는 무시)
    unique_per_user=False: 볼 때마다 이벤트 row 추가
    """
    # [Fix] 카테고리 ID 조회
    ai_news = db.get(AiGeneratedNews, ai_news_id)
    cat_id = ai_news.category_id if ai_news else None

    if not unique_per_user:
        db.add(NewsView(user_id=user_id, news_id=ai_news_id, category_id=cat_id, viewed_at=datetime.utcnow()))
        db.flush()
        return

    # 이미 있으면 viewed_at만 갱신(원하면 갱신 없이 return 해도 됨)
    existing = db.execute(
        select(NewsView).where(and_(NewsView.user_id == user_id, NewsView.news_id == ai_news_id))
    ).scalar_one_or_none()

    if existing:
        existing.viewed_at = datetime.utcnow()
        # 카테고리가 누락된 경우 업데이트
        if existing.category_id is None and cat_id is not None:
            existing.category_id = cat_id
        db.flush()
        return

    db.add(NewsView(user_id=user_id, news_id=ai_news_id, category_id=cat_id, viewed_at=datetime.utcnow()))
    db.flush()


def has_viewed(db: Session, *, user_id: int, ai_news_id: int) -> bool:
    row = db.execute(
        select(NewsView.news_view_id).where(and_(NewsView.user_id == user_id, NewsView.news_id == ai_news_id)).limit(1)
    ).first()
    return row is not None


# -------------------------
# Reactions (AiGeneratedNews 기준)
# -------------------------
def set_reaction(
    db: Session,
    *,
    user_id: int,
    ai_news_id: int,
    value: int,  # 1 or -1
) -> Tuple[str, int, int]:
    """
    좋아요/싫어요 토글 로직 + AiGeneratedNews의 like_count/dislike_count 동기화.
    반환: (status, like_count, dislike_count)
      status:
        - "set"      : 새로 설정
        - "switched" : like<->dislike 변경
        - "cleared"  : 같은 값 재클릭으로 취소
    """
    if value not in (1, -1):
        raise ValueError("value must be 1 or -1")

    ai = db.get(AiGeneratedNews, ai_news_id)
    if not ai:
        raise ValueError("AiGeneratedNews not found")

    r = db.execute(
        select(NewsReaction).where(and_(NewsReaction.user_id == user_id, NewsReaction.news_id == ai_news_id))
    ).scalar_one_or_none()

    # 없으면 새로 생성
    if r is None:
        db.add(NewsReaction(user_id=user_id, news_id=ai_news_id, value=value))
        if value == 1:
            ai.like_count += 1
        else:
            ai.dislike_count += 1
        db.flush()
        return ("set", ai.like_count, ai.dislike_count)

    # 같은 값을 누르면 취소
    if r.value == value:
        db.delete(r)
        if value == 1 and ai.like_count > 0:
            ai.like_count -= 1
        if value == -1 and ai.dislike_count > 0:
            ai.dislike_count -= 1
        db.flush()
        return ("cleared", ai.like_count, ai.dislike_count)

    # 반대 값으로 변경
    old = r.value
    r.value = value

    if old == 1 and ai.like_count > 0:
        ai.like_count -= 1
    if old == -1 and ai.dislike_count > 0:
        ai.dislike_count -= 1

    if value == 1:
        ai.like_count += 1
    else:
        ai.dislike_count += 1

    db.flush()
    return ("switched", ai.like_count, ai.dislike_count)


def get_reaction(db: Session, *, user_id: int, ai_news_id: int) -> Optional[int]:
    r = db.execute(
        select(NewsReaction.value).where(and_(NewsReaction.user_id == user_id, NewsReaction.news_id == ai_news_id))
    ).scalar_one_or_none()
    return r


def get_view_count(db: Session, *, news_id: int) -> int:
    """
    뉴스의 조회수 반환. (AiGeneratedNews id)
    """
    return db.query(NewsView).filter(NewsView.news_id == news_id).count()


def get_reaction_counts(db: Session, *, news_id: int) -> Dict[str, int]:
    """
    뉴스의 like/dislike 수 반환.
    """
    ai = db.get(AiGeneratedNews, news_id)
    if ai:
        return {"likes": ai.like_count, "dislikes": ai.dislike_count}

    # Fallback if news not found or relying on table count (though ai table is source of truth now)
    likes = db.query(NewsReaction).filter(NewsReaction.news_id == news_id, NewsReaction.value == 1).count()
    dislikes = db.query(NewsReaction).filter(NewsReaction.news_id == news_id, NewsReaction.value == -1).count()
    return {"likes": likes, "dislikes": dislikes}


# -------------------------
# Category subscriptions
# -------------------------
def get_category_name(db: Session, category_id: int) -> Optional[str]:
    """
    category_id로 카테고리 이름 조회
    """
    cat = db.get(Category, category_id)
    return cat.name if cat else None


def subscribe_category(db: Session, *, user_id: int, category_id: int) -> None:
    user = db.get(User, user_id)
    cat = db.get(Category, category_id)
    if not user or not cat:
        raise ValueError("user or category not found")

    if cat not in user.subscribed_categories:
        user.subscribed_categories.append(cat)
        db.flush()


def unsubscribe_category(db: Session, *, user_id: int, category_id: int) -> None:
    user = db.get(User, user_id)
    if not user:
        raise ValueError("user not found")
    user.subscribed_categories = [c for c in user.subscribed_categories if c.category_id != category_id]
    db.flush()


def list_subscribed_categories(db: Session, *, user_id: int) -> List[Category]:
    user = db.get(User, user_id)
    if not user:
        return []
    return list(user.subscribed_categories)


# -------------------------
# Keyword subscriptions (문자열)
# -------------------------
def subscribe_keyword(db: Session, *, user_id: int, keyword: str) -> None:
    keyword = normalize_keyword(keyword)
    if not keyword:
        raise ValueError("keyword is empty")

    existing = db.get(UserKeywordSubscription, {"user_id": user_id, "keyword": keyword})
    if existing:
        return

    db.add(UserKeywordSubscription(user_id=user_id, keyword=keyword))
    db.flush()


def unsubscribe_keyword(db: Session, *, user_id: int, keyword: str) -> int:
    keyword = normalize_keyword(keyword)
    if not keyword:
        return 0

    res = db.execute(
        delete(UserKeywordSubscription).where(
            and_(UserKeywordSubscription.user_id == user_id, UserKeywordSubscription.keyword == keyword)
        )
    )
    return res.rowcount or 0


def list_subscribed_keywords(db: Session, *, user_id: int) -> List[str]:
    return list(
        db.execute(select(UserKeywordSubscription.keyword).where(UserKeywordSubscription.user_id == user_id)).scalars()
    )


# -------------------------
# UserKeywordStat (읽은 기사 기반)
# -------------------------
def bump_user_keyword_stats_from_ai_news(
    db: Session,
    *,
    user_id: int,
    ai_news_id: int,
    inc: int = 1,
    keyword_limit: int = 200,
) -> int:
    """
    AiGeneratedNews.keywords(JSON 배열)를 읽어서 UserKeywordReadStat(user_id, keyword) count를 +inc.
    반환: 업데이트된 키워드 개수

    keyword_limit: 한 기사에서 처리할 최대 키워드 수(폭주 방지)
    """
    ai = db.get(AiGeneratedNews, ai_news_id)
    if not ai:
        raise ValueError("AiGeneratedNews not found")

    kws = ai.keywords or []
    if not isinstance(kws, list):
        return 0

    updated = 0
    for raw_kw in kws[:keyword_limit]:
        # [Fix] 문자열 또는 딕셔너리({"text": "...", "value": ...}) 처리
        kw_str = None
        if isinstance(raw_kw, str):
            kw_str = raw_kw
        elif isinstance(raw_kw, dict) and "text" in raw_kw:
            kw_str = raw_kw["text"]

        if not kw_str:
            continue

        kw = normalize_keyword(kw_str)
        if not kw:
            continue

        stat = db.get(UserKeywordReadStat, {"user_id": user_id, "keyword": kw})
        if stat:
            stat.count += inc
            stat.updated_at = datetime.utcnow()
        else:
            db.add(UserKeywordReadStat(user_id=user_id, keyword=kw, count=inc, updated_at=datetime.utcnow()))
        updated += 1

    db.flush()
    return updated


def list_user_top_keywords(db: Session, *, user_id: int, limit: int = 1000) -> List[Tuple[str, int]]:
    rows = db.execute(
        select(UserKeywordReadStat.keyword, UserKeywordReadStat.count)
        .where(UserKeywordReadStat.user_id == user_id)
        .order_by(UserKeywordReadStat.count.desc(), UserKeywordReadStat.updated_at.desc())
        .limit(limit)
    ).all()
    return [(r[0], r[1]) for r in rows]


# -------------------------
# Feed helpers (예시)
# -------------------------
def list_ai_news_feed_for_user(
    db: Session,
    *,
    user_id: int,
    limit: int = 50,
    exclude_viewed: bool = True,
) -> List[AiGeneratedNews]:
    """
    단순 예시: 최신 AiGeneratedNews를 가져오되, exclude_viewed면 이미 본 것 제외.
    (추천/구독 기반 필터는 여기서 추가하면 됨)
    """
    stmt = select(AiGeneratedNews).order_by(AiGeneratedNews.created_at.desc()).limit(limit)

    if exclude_viewed:
        viewed_subq = select(NewsView.news_id).where(NewsView.user_id == user_id).scalar_subquery()
        stmt = stmt.where(AiGeneratedNews.ai_generated_news_id.notin_(viewed_subq))

    return list(db.execute(stmt).scalars())


# -------------------------
# Search Log (검색 기록)
# -------------------------
def create_search_log(db: Session, *, user_id: int, query: str) -> SearchLog:
    """
    검색 기록 저장
    """
    log = SearchLog(user_id=user_id, query=query)
    db.add(log)
    db.flush()
    return log


def delete_search_log(db: Session, *, log_id: int) -> bool:
    """
    특정 검색 기록 삭제
    Returns: 삭제 성공 여부
    """
    log = db.get(SearchLog, log_id)
    if log:
        db.delete(log)
        db.flush()
        return True
    return False


def delete_user_search_logs(db: Session, *, user_id: int) -> int:
    """
    사용자의 모든 검색 기록 삭제
    Returns: 삭제된 개수
    """
    count = db.query(SearchLog).filter(SearchLog.user_id == user_id).delete()
    db.flush()
    return count


def get_user_search_logs(db: Session, *, user_id: int, limit: int = 20) -> List[SearchLog]:
    """
    사용자의 최근 검색 기록 조회
    """
    return (
        db.query(SearchLog)
        .filter(SearchLog.user_id == user_id)
        .order_by(SearchLog.searched_at.desc())
        .limit(limit)
        .all()
    )
