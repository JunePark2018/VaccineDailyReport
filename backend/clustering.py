import numpy as np
import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sentence_transformers import SentenceTransformer
import hdbscan
from sklearn.metrics.pairwise import cosine_similarity
# 최신 라이브러리 방식인 ModelInference 사용
from ibm_watsonx_ai.foundation_models import ModelInference

from database import SessionLocal, engine
from models import Base, Article, Issue

# -------------------------------------------------
# 1. 모델 로드 (Embedding & LLM)
# -------------------------------------------------
print("--- [AI] 모델 로딩 중... ---")
embed_model = SentenceTransformer("BAAI/bge-m3")

# Watsonx Llama-3-3-70b 설정 (llmtest.py에서 성공한 설정 반영)
credentials = {
    "apikey":  # 사용자님의 키 유지
    "url": "https://us-south.ml.cloud.ibm.com"
}

llm_model = ModelInference(
    model_id="meta-llama/llama-3-3-70b-instruct",
    credentials=credentials,
    project_id=
)

# -------------------------------------------------
# 2. Stage 2: LLM 검증 및 요약 함수
# -------------------------------------------------
def run_stage2_issue_refine(cluster_articles):
    titles = [a.title for a in cluster_articles]
    
    # [로그] 현재 검증 대상 출력
    print(f"\n      [LLM 검증 중] 기사 {len(titles)}건 후보 발견")
    for i, t in enumerate(titles[:3]): # 최대 3개만 미리보기
        print(f"        - {t}")
    if len(titles) > 3: print(f"        ... 외 {len(titles)-3}건")

    # 프롬프트 보강: 팩트 체크 및 인물 관계 명시 요청
    prompt = f"""
역할: 너는 뉴스 편집자다. 다음 뉴스 제목들이 '하나의 동일한 구체적 사건'인지 판단하라.
단순히 카테고리가 같은 것은 하나의 이슈가 아니다.

[뉴스 제목 목록]
{chr(10).join(f"- {t}" for t in titles)}

요청:
1. 이 묶음이 동일한 사건을 다루는지 판단하라 (is_issue: True/False)
2. 판단 이유를 적어라 (reason: ) - 예: 주체와 사건의 내용이 일치함 / 서로 다른 사건임
3. 동일 사건이라면 독자가 이해하기 쉬운 대표 제목을 생성하라 (title: )
4. 사건의 핵심을 2문장 이내로 요약하라 (summary: ) - 인물 관계(예: 교사-교사)를 정확히 명시할 것.

출력 형식:
is_issue: 
reason:
title: 
summary: 
"""
    try:
        # llmtest.py에서 성공한 파라미터 적용
        response = llm_model.generate_text(
            prompt=prompt,
            params={
                "max_new_tokens": 500,
                "temperature": 0.1, # 일관성을 위해 낮게 설정
                "decoding_method": "sample"
            }
        )
        
        # 파싱 로직
        res_dict = {}
        lines = response.strip().split('\n')
        for line in lines:
            if ':' in line:
                key, val = line.split(':', 1)
                res_dict[key.strip().lower()] = val.strip()
        
        # [로그] LLM의 판단 결과 출력
        status_icon = "✅" if res_dict.get('is_issue') == 'True' else "❌"
        print(f"      {status_icon} 결과: {res_dict.get('is_issue')}")
        print(f"      📝 이유: {res_dict.get('reason')}")
        if res_dict.get('is_issue') == 'True':
            print(f"      💡 생성된 제목: {res_dict.get('title')}")
            
        return res_dict
    except Exception as e:
        print(f"      ⚠️ [LLM Error] {e}")
        return None

# -------------------------------------------------
# 3. 메인 클러스터링 함수
# -------------------------------------------------
def run_issue_clustering(db: Session, days: int = 1):
    Base.metadata.create_all(bind=engine)

    # 미분류 기사 가져오기
    time_threshold = datetime.now() - timedelta(days=days)
    articles = db.query(Article).filter(
        Article.time >= time_threshold,
        Article.issue_id.is_(None)
    ).all()

    if len(articles) < 3:
        print(f"--- [Skip] 분류할 기사가 부족합니다. ({len(articles)}개) ---")
        return

    # [Stage 1] 임베딩 및 HDBSCAN
    print(f"--- [Stage 1] {len(articles)}개 기사 임베딩 생성 중... ---")
    # 제목 반복을 통해 고유명사 가중치 강화
    input_texts = [f"{a.title} {a.title} {(a.contents or '')[:50]}" for a in articles]
    embeddings = embed_model.encode(input_texts, normalize_embeddings=True)

    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=2,
        min_samples=1,
        metric="euclidean",
        cluster_selection_epsilon=0.35,
        cluster_selection_method="eom"
    )
    labels = clusterer.fit_predict(embeddings)

    unique_clusters = set(labels)
    print(f"--- [Stage 2] 후보 군집 검증 시작 ---")

    for cluster_id in unique_clusters:
        if cluster_id == -1: continue

        indices = np.where(labels == cluster_id)[0]
        cluster_articles = [articles[i] for i in indices]

        # [Stage 2] LLM에게 최종 확인 및 요약 요청
        refine_result = run_stage2_issue_refine(cluster_articles)

        if not refine_result or refine_result.get('is_issue') != 'True':
            print(f"   [Skip] LLM이 이슈가 아니라고 판단함 (기사 {len(cluster_articles)}건)")
            continue

        # [Step 6] 최종 DB 저장
        try:
            new_issue = Issue(
                title=refine_result.get('title', cluster_articles[0].title),
                contents=refine_result.get('summary', "요약 정보 없음"),
                analysis_result={
                    "status": "verified",
                    "article_count": len(cluster_articles),
                    "reason": refine_result.get('reason')
                },
                created_at=datetime.now()
            )
            db.add(new_issue)
            db.flush()

            for a in cluster_articles:
                a.issue_id = new_issue.id

            print(f"   ✅ 이슈 확정: {new_issue.title}")

        except Exception as e:
            db.rollback()
            print(f"   ❌ 저장 실패: {e}")

    db.commit()
    print("--- [Success] 클러스터링 및 검증 완료 ---")

if __name__ == "__main__":
    db = SessionLocal()
    try:
        run_issue_clustering(db, days=3)
    finally:
        db.close()