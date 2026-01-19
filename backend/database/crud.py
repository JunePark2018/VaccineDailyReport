# crud.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, List, Optional, Sequence, Tuple

from sqlalchemy import and_, delete, func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models import (
    Company,
    CompanyAlias,
    Cluster,
    News,
    AiGeneratedNews,
    User,
    Category,
    NewsReaction,
    NewsView,
    SearchLog,
    UserCategoryReadStat,
    UserKeywordStat,
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


def get_company_by_alias(db: Session, alias: str) -> Optional[Company]:
    alias = (alias or "").strip()
    ca = db.execute(select(CompanyAlias).where(CompanyAlias.alias == alias)).scalar_one_or_none()
    return ca.company if ca else None


def get_or_create_company_by_raw_name(
    db: Session,
    raw_company_name: str,
    display_name: Optional[str] = None,
) -> Company:
    """
    크롤러가 준 raw_company_name으로:
    1) alias 매칭되면 그 회사 반환
    2) 없으면 Company(name=raw) 생성 + CompanyAlias(alias=raw) 생성
    """
    raw = (raw_company_name or "").strip()
    if not raw:
        raise ValueError("raw_company_name is empty")

    # 1) alias로 먼저 찾기
    company = get_company_by_alias(db, raw)
    if company:
        return company

    # 2) Company.name으로도 찾기(혹시 표준명이 raw와 동일하게 이미 있음)
    company = get_company_by_name(db, raw)
    if company:
        # alias가 없었다면 alias만 추가
        try:
            with db.begin_nested():
                db.add(CompanyAlias(company_id=company.id, alias=raw))
                db.flush()
        except IntegrityError:
            db.rollback()
        return company

    # 3) 새로 만들기
    company = Company(name=raw, display_name=display_name)
    db.add(company)
    db.flush()  # company.id 확보

    db.add(CompanyAlias(company_id=company.id, alias=raw))
    db.flush()
    return company


def add_company_alias(db: Session, company_id: int, alias: str) -> CompanyAlias:
    alias = (alias or "").strip()
    if not alias:
        raise ValueError("alias is empty")

    obj = CompanyAlias(company_id=company_id, alias=alias)
    db.add(obj)
    db.flush()
    return obj


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
    region: str,  # "domestic" | "global"
    img_urls: Optional[dict | list] = None,
    created_at: Optional[datetime] = None,
) -> News:
    obj = News(
        title=title,
        contents=contents,
        url=url,
        company_id=company_id,
        region=region,
        img_urls=img_urls,
        created_at=created_at or datetime.utcnow(),
    )
    db.add(obj)
    db.flush()
    return obj


def get_news_by_url(db: Session, url: str) -> Optional[News]:
    return db.execute(select(News).where(News.url == url)).scalar_one_or_none()


def get_news(db: Session, news_id: int) -> Optional[News]:
    return db.get(News, news_id)


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
    created_at: Optional[datetime] = None,
) -> AiGeneratedNews:
    obj = AiGeneratedNews(
        cluster_id=cluster_id,
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
    db.flush()
    return obj


def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.get(User, user_id)


def get_user_by_login_id(db: Session, login_id: str) -> Optional[User]:
    return db.execute(select(User).where(User.login_id == login_id)).scalar_one_or_none()


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
    unique_per_user=True: (user_id, news_id) 이미 있으면 업데이트만(또는 무시)
    unique_per_user=False: 볼 때마다 이벤트 row 추가
    """
    if not unique_per_user:
        db.add(NewsView(user_id=user_id, news_id=ai_news_id, viewed_at=datetime.utcnow()))
        db.flush()
        return

    # 이미 있으면 viewed_at만 갱신(원하면 갱신 없이 return 해도 됨)
    existing = db.execute(
        select(NewsView).where(and_(NewsView.user_id == user_id, NewsView.news_id == ai_news_id))
    ).scalar_one_or_none()

    if existing:
        existing.viewed_at = datetime.utcnow()
        db.flush()
        return

    db.add(NewsView(user_id=user_id, news_id=ai_news_id, viewed_at=datetime.utcnow()))
    db.flush()


def has_viewed(db: Session, *, user_id: int, ai_news_id: int) -> bool:
    row = db.execute(
        select(NewsView.id).where(and_(NewsView.user_id == user_id, NewsView.news_id == ai_news_id)).limit(1)
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
        db.add(NewsReaction(user_id=user_id, news_id=ai_news_id, value=value, created_at=datetime.utcnow()))
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
    r.created_at = datetime.utcnow()

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


# -------------------------
# Category subscriptions
# -------------------------
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
    user.subscribed_categories = [c for c in user.subscribed_categories if c.id != category_id]
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

    db.add(UserKeywordSubscription(user_id=user_id, keyword=keyword, created_at=datetime.utcnow()))
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
        db.execute(
            select(UserKeywordSubscription.keyword)
            .where(UserKeywordSubscription.user_id == user_id)
            .order_by(UserKeywordSubscription.created_at.desc())
        ).scalars()
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
    AiGeneratedNews.keywords(JSON 배열)를 읽어서 UserKeywordStat(user_id, keyword) count를 +inc.
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
        if not isinstance(raw_kw, str):
            continue
        kw = normalize_keyword(raw_kw)
        if not kw:
            continue

        stat = db.get(UserKeywordStat, {"user_id": user_id, "keyword": kw})
        if stat:
            stat.count += inc
            stat.updated_at = datetime.utcnow()
        else:
            db.add(UserKeywordStat(user_id=user_id, keyword=kw, count=inc, updated_at=datetime.utcnow()))
        updated += 1

    db.flush()
    return updated


def list_user_top_keywords(db: Session, *, user_id: int, limit: int = 30) -> List[Tuple[str, int]]:
    rows = db.execute(
        select(UserKeywordStat.keyword, UserKeywordStat.count)
        .where(UserKeywordStat.user_id == user_id)
        .order_by(UserKeywordStat.count.desc(), UserKeywordStat.updated_at.desc())
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
        stmt = stmt.where(AiGeneratedNews.id.notin_(viewed_subq))

    return list(db.execute(stmt).scalars())
