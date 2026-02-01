import requests
import os
from dotenv import load_dotenv
from urllib.parse import quote
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Dict, Any, Optional, Union
from database.models import Report, News

# IBM WatsonX AI Import
from ibm_watsonx_ai.foundation_models import ModelInference

# Initialize IBM WatsonX Model
# ------------------------------------

load_dotenv(override=True)

credentials = {"apikey": os.getenv("WATSONX_API_KEY"), "url": os.getenv("WATSONX_URL")}

llm_model = ModelInference(
    model_id="meta-llama/llama-3-3-70b-instruct", credentials=credentials, project_id=os.getenv("WATSONX_PROJECT_ID")
)

# ------------------------------------


def get_llm_summary(prompt: str) -> str:
    """
    IBM WatsonX ModelInference를 사용하여 요약/분석을 생성합니다.
    """
    try:
        # Llama 3 프롬프트 형식에 맞춰주는 것이 좋음 (System/User)

        full_prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a helpful assistant that summarizes and analyzes text in Korean accurately and concisely.<|eot_id|><|start_header_id|>user<|end_header_id|>

{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>
"""

        # 파라미터 설정
        params = {"decoding_method": "greedy", "max_new_tokens": 1000, "min_new_tokens": 10, "repetition_penalty": 1.1}

        # 텍스트 생성
        response_text = llm_model.generate_text(prompt=full_prompt, params=params)
        return response_text.strip()

    except Exception as e:
        print(f"LLM Error: {e}")
        return "시스템 오류로 인해 AI 요약을 생성할 수 없습니다."





# 2. AI 요약(Issues) 검색 (Section 2)
def search_issues_by_keyword(db: Session, keyword: str) -> Dict[str, Any]:
    """
    DB AiGeneratedNews 테이블에서만 키워드가 포함된 이슈를 검색하고, LLM을 통해 분석합니다.
    (News 테이블은 참조하지 않음)
    """
    search_pattern = f"%{keyword}%"

    # Report 테이블 검색
    results = (
        db.query(Report)
        .filter(or_(Report.title.ilike(search_pattern), Report.contents.ilike(search_pattern)))
        .order_by(Report.created_at.desc())
        .limit(5)
        .all()
    )

    issues_list = [
        {
            "report_id": issue.report_id,
            "title": issue.title,
            "contents": issue.contents,
            "created_at": issue.created_at,
        }
        for issue in results
    ]

    # 이슈가 없으면 빈 결과 반환
    if not issues_list:
        return {"analysis": None, "issues": []}

    # LLM 분석을 위한 컨텍스트 구성
    prompt = f"사용자가 '{keyword}' 키워드로 검색했습니다. 다음은 관련된 최근 AI 뉴스 요약(Issue)들입니다:\n\n"

    for idx, item in enumerate(issues_list, 1):
        prompt += f"{idx}. 제목: {item['title']}\n내용: {item['contents'][:200]}...\n\n"

    prompt += (
        "위 내용(Issue)들을 바탕으로 트렌드나 핵심 내용을 종합적으로 분석하여 요약해 주세요. "
        "각 내용의 출처(제목)를 인용하며 자연스럽게 한국어로 설명해 주세요."
        "한자는 제외합니다. 포함될 시 한글로 번역합니다."
        "특수 기호는 제외합니다. 예시) *, #, @, $, %, ^, &, _, /, \, |, ;,{, }, `"
    )

    analysis_result = get_llm_summary(prompt)

    # ---------------------------------------------------------
    # [추가] 300자 내외로 최종 요양 및 최근 트렌드 강조
    # ---------------------------------------------------------
    refined_prompt = (
        f"다음은 '{keyword}'와 관련된 최근 주요 기사 분석 내용입니다:\n\n{analysis_result}\n\n"
        "위 내용을 바탕으로 최근 트렌드를 반영하여 **한글 300자 이내**로 아주 간결하게 핵심만 요약해 주세요. "
        "반드시 **하나의 단락(one paragraph)**으로만 작성해 주세요. 줄바꿈은 하지 않습니다. "
        "한자(Hanja)는 절대 사용하지 마세요. 모든 한자는 한글로 번역하여 표기해야 합니다. "
        "불필요한 수식어는 빼고 팩트 위주로 전달합니다. "
        "특수 기호(*, # 등)는 모두 제거하고 평문으로 작성합니다."
    )
    
    analysis_result = get_llm_summary(refined_prompt)

    return {"analysis": analysis_result, "issues": issues_list}


def deduplicate_articles(articles: List[News], limit: int) -> List[News]:
    """
    기사 리스트에서 중복을 제거하고 대표 기사만 추려냅니다.
    1. issue_id가 있는 경우: 같은 이슈 그룹 중 가장 최신 기사 1개만 선택
    2. issue_id가 없는 경우: 그대로 유지 (단, 제목이 완전히 같다면 제거)
    """
    seen_ids = set()
    unique_articles = []

    # 제목 중복 방지용
    seen_titles = set()

    for art in articles:
        # 이미 충분한 수량이 모였으면 중단
        if len(unique_articles) >= limit:
            break

        # 1. 제목 완전 일치 중복 제거
        if art.title in seen_titles:
            continue
        seen_titles.add(art.title)

        # 2. 이슈 그룹 중복 제거
        if art.news_id in seen_ids:
            continue  # 이미 이 이슈의 기사가 하나 들어갔으므로 스킵
        seen_ids.add(art.news_id)

        # 통과한 기사 추가
        unique_articles.append(art)

    return unique_articles


# 3. 핫토픽(Articles) 검색 (Section 3)
def search_hot_topics_by_keyword(db: Session, keyword: str) -> List[Dict[str, Any]]:
    """
    DB News 테이블에서 키워드가 포함되고 이미지가 있는 기사를 검색합니다.
    """
    search_pattern = f"%{keyword}%"

    articles = (
        db.query(News)
        .filter(or_(News.title.ilike(search_pattern), News.contents.ilike(search_pattern)))
        .order_by(News.created_at.desc())
        .limit(100)
        .all()
    )

    # 중복 제거 로직 적용 (최대 10개)
    unique_articles = deduplicate_articles(articles, limit=10)

    hot_topics = []
    for art in unique_articles:
        if art.img_urls and len(art.img_urls) > 0:
            hot_topics.append(
                {
                    "news_id": art.news_id,
                    "title": art.title,
                    "img_urls": art.img_urls,
                    "url": art.url,
                    "company_name": art.company.name,
                }
            )

    return hot_topics


# 4. 일반 기사 검색 (Related News용) (Section 3)
def search_articles_by_keyword(db: Session, keyword: str) -> List[Dict[str, Any]]:
    """
    DB News 테이블에서 키워드가 포함된 기사를 검색합니다.
    """
    search_pattern = f"%{keyword}%"

    articles = (
        db.query(News)
        .filter(or_(News.title.ilike(search_pattern), News.contents.ilike(search_pattern)))
        .order_by(News.created_at.desc())  # time → created_at
        .limit(100)  # 필터링 위해 넉넉히
        .all()
    )

    # 중복 제거 로직 적용 (최대 20개)
    unique_articles = deduplicate_articles(articles, limit=20)

    return [
        {"news_id": art.news_id, "title": art.title, "url": art.url, "company_name": art.company_name, "view_count": 0}
        for art in unique_articles
    ]
