"""
AI 생성 뉴스 관련 라우터
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_

from routers import get_db
from database.models import AiGeneratedNews, Cluster

# schemas import 제거 - dict 반환으로 충분

router = APIRouter(prefix="/generated-news", tags=["AI Generated News"])


@router.get("")
def get_generated_news(
    skip: int = 0,
    limit: int = 10,
    category_id: Optional[int] = Query(None, description="카테고리 ID로 필터링"),
    db: Session = Depends(get_db),
):
    """
    AI가 생성한 뉴스들을 가져옵니다.

    **skip**: 앞에서부터 건너뛸 데이터의 개수 (페이지 번호 구현 시 사용)<br/>
    **limit**: 한 번에 가져올 최대 데이터 개수 (페이지 당 목록 수)<br/>
    **category_id**: (선택) 특정 카테고리로 필터링<br/>
    """

    query = db.query(AiGeneratedNews).options(joinedload(AiGeneratedNews.category))

    if category_id is not None:
        query = query.filter(AiGeneratedNews.category_id == category_id)

    results = query.order_by(AiGeneratedNews.created_at.desc()).offset(skip).limit(limit).all()

    # 카테고리 이름 포함하여 반환
    response_data = []
    for item in results:
        # keywords가 JSON이면 string으로 변환
        keywords_value = item.keywords
        if isinstance(keywords_value, (dict, list)):
            import json

            keywords_value = json.dumps(keywords_value, ensure_ascii=False)

        item_dict = {
            "id": item.id,
            "cluster_id": item.cluster_id,
            "category_id": item.category_id,
            "category_name": item.category.name if item.category else None,
            "title": item.title,
            "contents": item.contents,
            "created_at": item.created_at,
            "analysis_result": item.analysis_result,
            "keywords": keywords_value,
            "like_count": item.like_count,
            "dislike_count": item.dislike_count,
        }
        response_data.append(item_dict)

    return response_data


@router.get("/search")
def search_generated_news(
    keyword: str = Query(..., min_length=1, description="검색어"),
    category_id: Optional[int] = Query(None, description="카테고리 ID로 필터링"),
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    """
    AI가 생성한 뉴스에서 '내용(contents)' 또는 '제목(title)'에 키워드가 포함된 뉴스를 찾습니다.

    **keyword**: 검색할 키워드.<br/>
    **category_id**: (선택) 특정 카테고리로 필터링<br/>
    **skip**: 앞에서부터 건너뛸 데이터의 개수 (페이지 번호 구현 시 사용)<br/>
    **limit**: 한 번에 가져올 최대 데이터 개수 (페이지 당 목록 수)<br/>
    """

    search_pattern = f"%{keyword}%"

    query = (
        db.query(AiGeneratedNews)
        .options(joinedload(AiGeneratedNews.category))
        .filter(or_(AiGeneratedNews.title.ilike(search_pattern), AiGeneratedNews.contents.ilike(search_pattern)))
    )

    if category_id is not None:
        query = query.filter(AiGeneratedNews.category_id == category_id)

    results = query.offset(skip).limit(limit).all()

    if results:
        response_data = []
        for item in results:
            # keywords가 JSON이면 string으로 변환
            keywords_value = item.keywords
            if isinstance(keywords_value, (dict, list)):
                import json

                keywords_value = json.dumps(keywords_value, ensure_ascii=False)

            item_dict = {
                "id": item.id,
                "cluster_id": item.cluster_id,
                "category_id": item.category_id,
                "category_name": item.category.name if item.category else None,
                "title": item.title,
                "contents": item.contents,
                "created_at": item.created_at,
                "analysis_result": item.analysis_result,
                "keywords": keywords_value,
                "like_count": item.like_count,
                "dislike_count": item.dislike_count,
            }
            response_data.append(item_dict)
        return response_data

    return []


@router.get("/{generated_news_id}")
def get_generated_news_detail(generated_news_id: int, db: Session = Depends(get_db)):
    """
    AI가 생성한 뉴스 중 특정 ID에 해당하는 뉴스를 가져옵니다.

    **generated_news_id**: AI가 생성한 뉴스의 ID.
    """

    generated_news = (
        db.query(AiGeneratedNews)
        .options(joinedload(AiGeneratedNews.cluster).joinedload(Cluster.news), joinedload(AiGeneratedNews.category))
        .filter(AiGeneratedNews.id == generated_news_id)
        .first()
    )

    if not generated_news:
        raise HTTPException(status_code=404, detail="해당 뉴스를 찾을 수 없습니다.")

    # keywords가 JSON이면 string으로 변환
    keywords_value = generated_news.keywords
    if isinstance(keywords_value, (dict, list)):
        import json

        keywords_value = json.dumps(keywords_value, ensure_ascii=False)

    return {
        "id": generated_news.id,
        "cluster_id": generated_news.cluster_id,
        "category_id": generated_news.category_id,
        "category_name": generated_news.category.name if generated_news.category else None,
        "title": generated_news.title,
        "contents": generated_news.contents,
        "created_at": generated_news.created_at,
        "analysis_result": generated_news.analysis_result,
        "keywords": keywords_value,
        "like_count": generated_news.like_count,
        "dislike_count": generated_news.dislike_count,
        "cluster": generated_news.cluster,
    }
