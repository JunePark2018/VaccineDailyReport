import numpy as np
import re
import chromadb
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sentence_transformers import SentenceTransformer
import hdbscan
from sklearn.metrics.pairwise import cosine_similarity
from ibm_watsonx_ai.foundation_models import ModelInference
from sklearn.preprocessing import normalize 
from database import SessionLocal, engine
from models import Base, Article, Issue

# -------------------------------------------------
# 1. 모델 및 벡터 DB 초기화
# -------------------------------------------------
print("--- [AI] 모델 및 ChromaDB 로딩 중... ---")
embed_model = SentenceTransformer("BAAI/bge-m3")
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="news_articles")

credentials = {
    "apikey": "",
    "url": "https://us-south.ml.cloud.ibm.com/"
}

llm_model = ModelInference(
    model_id="meta-llama/llama-3-3-70b-instruct",
    credentials=credentials,
    project_id=""
)

# -------------------------------------------------
# 2. 보조 함수 정의
# -------------------------------------------------
def get_embeddings_with_cache(articles):
    article_ids = [str(a.id) for a in articles]
    existing_data = collection.get(ids=article_ids, include=['embeddings'])
    existing_ids = set(existing_data['ids'])
    
    needed_articles = [a for a in articles if str(a.id) not in existing_ids]
    if needed_articles:
        print(f"      [Cache] 본문 포함 {len(needed_articles)}건 임베딩 생성 중...")
        texts = [f"제목: {a.title} 내용: {(a.contents or '')[:200]}" for a in needed_articles]
        new_embeddings = embed_model.encode(texts, normalize_embeddings=True).tolist()
        collection.add(
            ids=[str(a.id) for a in needed_articles],
            embeddings=new_embeddings,
            metadatas=[{"title": a.title} for a in needed_articles]
        )
    
    final_data = collection.get(ids=article_ids, include=['embeddings'])
    id_to_embedding = {idx: emb for idx, emb in zip(final_data['ids'], final_data['embeddings'])}
    return np.array([id_to_embedding[str(a.id)] for a in articles])

def simple_kg_check(articles):
    if len(articles) < 2: return True
    generic_words = {'오늘', '내일', '속보', '단독', '종합', '포토', '영상', '게시', '출시', '진행', '개최', 
                     '사고', '발생', '사망', '부상', '혐의', '검거', '확인', '관련', '명과', '명이', '명은'}

    def get_clean_keywords(text):
        words = re.findall(r'[가-힣A-Za-z]{2,}', text)
        return set([w for w in words if w not in generic_words])

    base_entities = get_clean_keywords(articles[0].title)
    for other in articles[1:]:
        target_entities = get_clean_keywords(other.title)
        if len(base_entities.intersection(target_entities)) >= 1:
            continue
        return False
    return True

def run_stage2_issue_refine(cluster_articles):
    article_summaries = []
    for a in cluster_articles[:10]:
        clean_content = re.sub(r'\s+', ' ', (a.contents or ''))[:150]
        article_summaries.append(f"제목: {a.title}\n요약: {clean_content}")

    prompt = f"""
역할: 뉴스 분석 전문가.
목표: 아래 기사들이 '동일한 구체적 사건' 혹은 '직접적으로 이어진 후속 보도'인지 판단하라.

[분석 가이드]
1. 인물/조직: 기사에 등장하는 주체(사람 이름, 기업명, 국가 등)가 일치하는가?
2. 장소/대상: 사건이 벌어진 구체적 장소나 대상물이 같은가?
3. 인과관계: 앞 기사의 결과로 뒤 기사가 발생했는가?

[주의] 단순히 카테고리가 같다고 해서 같은 이슈로 묶지 마라. 

[기사 목록]
{chr(10).join(article_summaries)}

[출력 형식]
is_issue: (True/False)
reason: (판단 이유)
title: (대표 제목)
"""
    try:
        response = llm_model.generate_text(
            prompt=prompt,
            params={"max_new_tokens": 400, "temperature": 0.1}
        )
        res_dict = {}
        for line in response.strip().split('\n'):
            if ':' in line:
                key, val = line.split(':', 1)
                res_dict[key.strip().lower().replace('*', '')] = val.strip().replace('*', '')
        
        is_issue_val = res_dict.get('is_issue', 'FALSE').upper()
        res_dict['is_issue'] = 'True' if 'TRUE' in is_issue_val else 'False'
        return res_dict
    except Exception as e:
        print(f"      ⚠️ [LLM Error] {e}")
        return {"is_issue": "False", "reason": "Error"}

def save_issue_to_db(db: Session, res: dict, cluster_articles: list):
    new_issue = Issue(
        title=res.get('title', cluster_articles[0].title),
        created_at=datetime.now()
    )
    db.add(new_issue)
    db.flush() 
    for article in cluster_articles:
        article.issue_id = new_issue.id
    print(f"      ✨ 이슈 생성: {new_issue.title} ({len(cluster_articles)}건)")

# -------------------------------------------------
# 3. 메인 클러스터링 로직
# -------------------------------------------------
def run_issue_clustering(db: Session, days: int = 3):
    Base.metadata.create_all(bind=engine)
    time_threshold = datetime.now() - timedelta(days=days)
    articles = db.query(Article).filter(Article.time >= time_threshold, Article.issue_id.is_(None)).all()

    if len(articles) < 2:
        return

    all_embeddings = np.array(get_embeddings_with_cache(articles)).astype('float32')

    # 1. 기존 이슈 매칭
    recent_issues = db.query(Issue).filter(Issue.created_at >= time_threshold).all()
    for issue in recent_issues:
        sample = db.query(Article).filter(Article.issue_id == issue.id).first()
        if not sample: continue
        
        res = collection.get(ids=[str(sample.id)], include=['embeddings'])
        
        # [ValueError 해결] NumPy 배열의 비어있음을 확인하는 더 정확한 방법
        target_embs = res.get('embeddings')
        if target_embs is None or len(target_embs) == 0:
            continue
        
        issue_vec = np.array(target_embs[0]).reshape(1, -1)
        for i, article in enumerate(articles):
            if article.issue_id is not None: continue
            sim = cosine_similarity(all_embeddings[i].reshape(1, -1), issue_vec)[0][0]
            if sim > 0.85:
                article.issue_id = issue.id

    # 2. 신규 군집화
    rem_idx = [i for i, a in enumerate(articles) if a.issue_id is None]
    rem_arts = [articles[i] for i in rem_idx]
    if len(rem_arts) < 2:
        db.commit()
        return

    rem_embs = all_embeddings[rem_idx]
    norm_embs = normalize(rem_embs)

    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=2,
        min_samples=1,
        metric='euclidean',
        cluster_selection_epsilon=0.4
    )
    labels = clusterer.fit_predict(norm_embs)

    # 3. 검증 및 저장
    for cid in set(labels):
        if cid == -1: continue
        c_articles = [rem_arts[i] for i in np.where(labels == cid)[0]]
        if not simple_kg_check(c_articles): continue
        
        res = run_stage2_issue_refine(c_articles)
        if res and res.get('is_issue') == 'True':
            save_issue_to_db(db, res, c_articles)

    db.commit()
    print("--- [Success] 클러스터링 완료 ---")

if __name__ == "__main__":
    db = SessionLocal()
    try:
        run_issue_clustering(db, days=3)
    finally:
        db.close()