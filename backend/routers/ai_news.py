"""
AI 생성 뉴스 관련 라우터
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_

# ... (other imports are fine, but I need to make sure I match the file content structure.
# The previous `from sqlalchemy import or_` was on line 8.
# I will edit the import line separately or include it in the replace if I can span that far, but the file is large. 
# Better to do two edits or use multi_replace.
# I will use multi_replace to handle both the import and the function body safely.

# actually I will just use replace_file_content for the import first, then the function.
# Wait, I can do it in one multi_replace.


from routers import get_db
from database.models import AiGeneratedNews, Cluster
from database import crud

# schemas import 제거 - dict 반환으로 충분
from pydantic import BaseModel

class CitationRequest(BaseModel):
    cluster_id: int
    target_sentence: str

# -----------------------------------------------------------
# [Deep Citation Agent] Logic
# -----------------------------------------------------------
def split_sentences_positions(text: str):
    """
    텍스트를 문장 단위로 분리하고, 원본 텍스트 내의 위치(시작 인덱스 등)를 추적하거나
    최소한 '어느 문장이냐'를 리스트로 반환.
    여기서는 단순 split 후 strip 처리.
    """
    if not text:
        return []
    # 마침표, 물음표, 느낌표 뒤에 공백이 있는 경우 분리
    import re
    # 단순화된 정규식: 문장 종결 부호(.!?) 뒤에 공백 혹은 문자열 끝
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]

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
            "ai_generated_news_id": item.ai_generated_news_id,
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
                "ai_generated_news_id": item.ai_generated_news_id,
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
        .filter(AiGeneratedNews.ai_generated_news_id == generated_news_id)
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
        "ai_generated_news_id": generated_news.ai_generated_news_id,
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
        # "cluster": generated_news.cluster, # 순환 참조 주의, 필요한 경우 serialize
    }


@router.get("/clusters/{cluster_id}/news")
def read_cluster_news(cluster_id: int, db: Session = Depends(get_db)):
    """
    클러스터 ID를 받아서 연결된 원본 기사 목록(제목, URL, 언론사명)을 반환합니다.
    """
    original_news_list = crud.get_original_news_details_by_cluster(db, cluster_id)

    return original_news_list


@router.post("/citation")
def check_citation(req: CitationRequest, db: Session = Depends(get_db)):
    """
    [Deep Citation Agent]
    특정 문장이 주어졌을 때, 해당 클러스터에 연결된 원본 기사들 중에서
    가장 유사한 문장(근거)을 찾아 반환합니다. (On-Demand Vector Search)
    """
    from database.vector_store import encode_texts
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np

    # 1. 원본 기사 가져오기
    original_news_list = crud.get_original_news_details_by_cluster(db, req.cluster_id)
    if not original_news_list:
        return {"match_found": False, "message": "원본 기사가 없습니다."}

    # 2. 모든 기사의 문장을 추출하여 후보군(Corpus) 생성
    candidates = []
    # candidates 구조: { "text": 문장, "doc_title": 기사제목, "company": 언론사, "url": 기사URL }

    for news in original_news_list:
        sentences = split_sentences_positions(str(news["contents"]))
        for s in sentences:
            if len(s) < 10: continue # 너무 짧은 문장은 제외
            candidates.append({
                "text": s,
                "doc_title": news["title"],
                "company": news["company_name"],
                "url": news["url"]
            })
    
    if not candidates:
        return {"match_found": False, "message": "비교할 문장이 없습니다."}

    # 3. 임베딩 생성 (Target 1개 + Candidates N개)
    #    속도 최적화를 위해 한 번에 encoding
    all_texts = [req.target_sentence] + [c["text"] for c in candidates]
    
    # vector_store의 encode_texts 사용
    embeddings = encode_texts(all_texts)
    
    target_vec = embeddings[0].reshape(1, -1)
    candidate_vecs = embeddings[1:]

    # 4. 유사도 계산
    sim_scores = cosine_similarity(target_vec, candidate_vecs)[0]

    # 5. Top 3 추출
    # argsort는 오름차순이므로 뒤집어야 함
    top_indices = sim_scores.argsort()[::-1][:3]
    
    results = []
    for idx in top_indices:
        score = float(sim_scores[idx])
        if score < 0.3: # 유사도 너무 낮으면 무시 (Threshold)
            continue
            
        match_item = candidates[idx]
        results.append({
            "score": round(score * 100, 1),
            "text": match_item["text"],
            "company": match_item["company"],
            "doc_title": match_item["doc_title"],
            "url": match_item["url"]
        })

    return {
        "match_found": len(results) > 0,
        "matches": results
    }


@router.get("/{generated_news_id}/related")
def get_related_news(generated_news_id: int, limit: int = 3, db: Session = Depends(get_db)):
    """
    특정 AI 뉴스와 연관된(키워드가 유사한) 다른 AI 뉴스들을 추천합니다.
    [Fallback Logic]
    1. Top 3 키워드를 모두 포함하는 기사 검색
    2. 부족하면 Top 2 키워드를 모두 포함하는 기사 검색
    3. 부족하면 Top 1 키워드를 포함하는 기사 검색
    """
    # 1. 현재 뉴스 조회
    current_news = db.get(AiGeneratedNews, generated_news_id)
    if not current_news:
        raise HTTPException(status_code=404, detail="News not found")

    # 2. 키워드 추출
    if not current_news.keywords:
        return []

    current_kws = current_news.keywords
    if isinstance(current_kws, str):
        import json
        try:
            current_kws = json.loads(current_kws)
        except:
            current_kws = []

    try:
        sorted_kws = sorted(current_kws, key=lambda x: x.get("value", 0), reverse=True)
        # 상위 3개 단어 텍스트 추출
        all_top_keywords = [k.get("text") for k in sorted_kws if k.get("text")]
    except Exception as e:
        print(f"Error parsing keywords: {e}")
        return []

    if not all_top_keywords:
        return []

    final_results = []
    excluded_ids = {generated_news_id}  # 자기 자신 제외

    # 3. Tiered Search Strategy (3 keywords -> 2 keywords -> 1 keyword)
    # 최대 3개까지만 시도 (키워드가 적으면 그만큼만)
    max_k = min(len(all_top_keywords), 3)
    
    # 3부터 1까지 역순으로 시도 (예: 3, 2, 1)
    for k_count in range(max_k, 0, -1):
        if len(final_results) >= limit:
            break

        needed = limit - len(final_results)
        target_keywords = all_top_keywords[:k_count]
        
        # 쿼리 생성: (제목이나 내용에 k1 포함) AND (제목이나 내용에 k2 포함) ...
        # excluded_ids에 없는 것만
        query = db.query(AiGeneratedNews).filter(AiGeneratedNews.ai_generated_news_id.notin_(excluded_ids))
        
        # AND 조건 추가
        conditions = []
        for kw in target_keywords:
            pattern = f"%{kw}%"
            conditions.append(or_(AiGeneratedNews.title.ilike(pattern), AiGeneratedNews.contents.ilike(pattern)))
        
        if conditions:
            query = query.filter(and_(*conditions))
        
        # 최신순 정렬하여 필요한 만큼 가져오기
        tier_results = query.order_by(AiGeneratedNews.created_at.desc()).limit(needed).all()

        for item in tier_results:
            final_results.append(item)
            excluded_ids.add(item.ai_generated_news_id)

    # 4. 결과 포맷팅
    response_data = []
    for item in final_results:
        # 이미지 URL 로드 logic (Lazy load)
        img_url = None
        if item.cluster and item.cluster.news:
            for origin_news in item.cluster.news:
                if origin_news.img_urls:
                    urls = origin_news.img_urls
                    if isinstance(urls, str):
                        import json
                        try:
                            urls = json.loads(urls)
                        except:
                            urls = []
                    
                    if isinstance(urls, list) and len(urls) > 0:
                        img_url = urls[0]
                        break
        
        summary = item.contents[:40] + "..." if item.contents and len(item.contents) > 40 else item.contents
        
        response_data.append({
            "id": item.ai_generated_news_id,
            "title": item.title,
            "image_url": img_url,
            "contents_short": summary
        })

    return response_data
