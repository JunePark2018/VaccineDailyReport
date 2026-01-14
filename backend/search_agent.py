import requests
import os
from urllib.parse import quote
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Dict, Any, Optional, Union
from models import Issue, Article

# IBM WatsonX AI Import
from ibm_watsonx_ai.foundation_models import ModelInference

# Initialize IBM WatsonX Model
credentials = {
    "apikey": "", 
    "url": "https://us-south.ml.cloud.ibm.com/"
}

llm_model = ModelInference(
    model_id="meta-llama/llama-3-3-70b-instruct",
    credentials=credentials,
    project_id=
)

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
        params = {
            "decoding_method": "greedy",
            "max_new_tokens": 1000, 
            "min_new_tokens": 10,
            "repetition_penalty": 1.1
        }
        
        # 텍스트 생성
        response_text = llm_model.generate_text(prompt=full_prompt, params=params)
        return response_text.strip()

    except Exception as e:
        print(f"LLM Error: {e}")
        return "시스템 오류로 인해 AI 요약을 생성할 수 없습니다."

# 1. 위키피디아 검색 (Section 1)
def search_wikipedia(keyword: str) -> Optional[Dict[str, str]]:
    """
    위키피디아 API를 통해 정의와 요약을 가져온 후, LLM을 통해 내용을 정리합니다.
    API 검색 실패 시 None을 반환합니다.
    (개선: 키워드로 먼저 '검색'하여 가장 적절한 문서 제목을 찾은 뒤 요약을 가져옴)
    """
    
    # 1. 관련 문서 제목 검색 (Opensearch API 사용)
    search_url = "https://ko.wikipedia.org/w/api.php"
    search_params = {
        "action": "opensearch",
        "search": keyword,
        "limit": 1,
        "namespace": 0,
        "format": "json"
    }
    
    # Headers - 위키피디아 정책 준수
    headers = {
        'User-Agent': 'VaccineDailyReportBot/1.0 (contact@example.com)'
    }
    
    target_title = keyword # 기본값은 입력받은 그대로
    
    try:
        search_res = requests.get(search_url, params=search_params, headers=headers, timeout=5)
        if search_res.status_code == 200:
            search_data = search_res.json()
            if search_data and len(search_data) > 1 and search_data[1]:
                target_title = search_data[1][0] 
    except Exception as e:
        print(f"Wikipedia Search API Error: {e}")

    # 2. 해당 제목(target_title)으로 요약 정보 가져오기
    encoded_keyword = quote(target_title)
    url = f"https://ko.wikipedia.org/api/rest_v1/page/summary/{encoded_keyword}"
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            
            # 'type' 체크를 완화하고, title과 extract가 있는지 확인
            # 'disambiguation' (동음이의어 문서) 타입은 제외할 수 있으나, 
            # 사용자 요구에 따라 일단 정보가 있으면 보여줌.
            if data.get("title") and data.get("extract"):
                raw_summary = data.get("extract")
                
                # LLM을 이용해 내용을 정리 (1차 정보 전달)
                llm_prompt = (
                    f"다음은 위키피디아의 '{target_title}'에 대한 요약 내용입니다. "
                    "위키피디아의 정보를 정확하게 전달해야 합니다."
                    f"이 내용을 읽기 쉽게 핵심만 정리해서 한국어로 설명해 주세요:\n\n{raw_summary}"
                )
                
                llm_summary = get_llm_summary(llm_prompt)
                
                return {
                    "title": data.get("title"),
                    "summary": llm_summary, 
                    "original_summary": raw_summary, 
                    "url": data.get("content_urls", {}).get("desktop", {}).get("page")
                }
    except Exception as e:
        print(f"Wikipedia Summary API Error: {e}")
    
    return None

# 2. AI 요약(Issues) 검색 (Section 2)
def search_issues_by_keyword(db: Session, keyword: str) -> Dict[str, Any]:
    """
    DB Issue 테이블에서만 키워드가 포함된 이슈를 검색하고, LLM을 통해 분석합니다.
    (Article 테이블은 참조하지 않음)
    """
    search_pattern = f"%{keyword}%"
    
    # Issue 테이블 검색
    results = db.query(Issue).filter(
        or_(
            Issue.title.ilike(search_pattern),
            Issue.contents.ilike(search_pattern)
        )
    ).order_by(Issue.created_at.desc()).limit(5).all()
    
    issues_list = [
        {
            "id": issue.id,
            "title": issue.title,
            "contents": issue.contents,
            "created_at": issue.created_at
        } 
        for issue in results
    ]
    
    # 이슈가 없으면 빈 결과 반환
    if not issues_list:
        return {
            "analysis": None,
            "issues": []
        }

    # LLM 분석을 위한 컨텍스트 구성
    prompt = f"사용자가 '{keyword}' 키워드로 검색했습니다. 다음은 관련된 최근 AI 뉴스 요약(Issue)들입니다:\n\n"
    
    for idx, item in enumerate(issues_list, 1):
        prompt += f"{idx}. 제목: {item['title']}\n내용: {item['contents'][:200]}...\n\n"
        
    prompt += (
        "위 내용(Issue)들을 바탕으로 트렌드나 핵심 내용을 종합적으로 분석하여 요약해 주세요. "
        "각 내용의 출처(제목)를 인용하며 자연스럽게 한국어로 설명해 주세요."
        "한자는 제외합니다. 포함될 시 한글로 번역합니다."
        "위키피디아의 내용을 근거로 참고해도 좋습니다."
        "특수 기호는 제외합니다. 예시) *, #, @, $, %, ^, &, _, /, \, |, ;,{, }, `"
    )
    
    analysis_result = get_llm_summary(prompt)
    
    return {
        "analysis": analysis_result,
        "issues": issues_list
    }

# 3. 핫토픽(Articles) 검색 (Section 3)
def search_hot_topics_by_keyword(db: Session, keyword: str) -> List[Dict[str, Any]]:
    """
    DB Article 테이블에서 키워드가 포함되고 이미지가 있는 기사를 검색합니다.
    """
    search_pattern = f"%{keyword}%"
    
    articles = db.query(Article).filter(
        or_(
            Article.title.ilike(search_pattern),
            Article.contents.ilike(search_pattern)
        )
    ).order_by(Article.time.desc()).limit(50).all()
    
    hot_topics = []
    for art in articles:
        if art.img_urls and len(art.img_urls) > 0:
            hot_topics.append({
                "id": art.id,
                "title": art.title,
                "img_urls": art.img_urls,
                "url": art.url,
                "company_name": art.company_name
            })
            if len(hot_topics) >= 10: 
                break
                
    return hot_topics

# 4. 일반 기사 검색 (Related News용) (Section 3)
def search_articles_by_keyword(db: Session, keyword: str) -> List[Dict[str, Any]]:
    """
    DB Article 테이블에서 키워드가 포함된 기사를 검색합니다.
    """
    search_pattern = f"%{keyword}%"
    
    articles = db.query(Article).filter(
        or_(
            Article.title.ilike(search_pattern),
            Article.contents.ilike(search_pattern)
        )
    ).order_by(Article.time.desc()).limit(20) # 최대 20개
    
    # 쿼리 결과 사용
    
    return [
        {
            "id": art.id,
            "title": art.title,
            "url": art.url,
            "company_name": art.company_name,
            "view_count": 0 
        }
        for art in articles 
    ]
