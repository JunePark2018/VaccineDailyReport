"""
원본 뉴스 관련 라우터
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_

from routers import get_db
from database.models import News
from schemas import NewsResponse

router = APIRouter(prefix="/news", tags=["Original News"])


@router.get("", response_model=List[NewsResponse])
def get_news(skip: int = 0, limit: int = 20, region: Optional[str] = None, db: Session = Depends(get_db)):
    """
    크롤링한 뉴스들을 가져옵니다.

    **skip**: 앞에서부터 건너뛸 데이터의 개수 (페이지 번호 구현 시 사용)<br/>
    **limit**: 한 번에 가져올 최대 데이터 개수 (페이지 당 목록 수)<br/>
    **region**: 한정할 지역 ("domestic" or "global")
    """
    query = db.query(News).options(joinedload(News.company))

    if region:
        query = query.filter(News.region == region)

    return query.order_by(News.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/search", response_model=List[NewsResponse])
def search_news(
    keyword: str = Query(..., min_length=1, description="검색어"),
    region: Optional[str] = None,
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

    query = db.query(News)

    if region:
        query = query.filter(News.region == region)

    search_pattern = f"%{keyword}%"
    query = query.filter(or_(News.title.ilike(search_pattern), News.contents.ilike(search_pattern)))

    results = query.order_by(News.created_at.desc()).offset(skip).limit(limit).all()

    return results


@router.get("/{news_id}", response_model=NewsResponse)
def get_news_detail(news_id: int, db: Session = Depends(get_db)):
    """
    크롤링한 뉴스들 중 특정 ID에 해당하는 뉴스를 가져옵니다.

    **id**: 뉴스의 ID.
    """
    news = db.query(News).filter(News.id == news_id).first()

    if news is None:
        raise HTTPException(status_code=404, detail="뉴스를 찾을 수 없습니다.")

    return news
