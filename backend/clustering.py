import numpy as np
import re
import os
from dotenv import load_dotenv # 추가
import chromadb
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sentence_transformers import SentenceTransformer
import hdbscan
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize
from ibm_watsonx_ai.foundation_models import ModelInference
from kiwipiepy import Kiwi

from database.engine import SessionLocal, engine
from database.models import Base, Article, Issue


load_dotenv()
kiwi = Kiwi()
WATSONX_API_KEY = os.getenv("WATSONX_API_KEY")
WATSONX_PROJECT_ID = os.getenv("WATSONX_PROJECT_ID")
WATSONX_URL = os.getenv("WATSONX_URL")
# -------------------------------------------------
# 1. 초기화 및 ChromaDB 설정 (전문 벡터 DB)
# -------------------------------------------------
print("--- [AI] 모델 및 ChromaDB 로딩 중... ---")
embed_model = SentenceTransformer("jhgan/ko-sroberta-multitask")

# ChromaDB 물리적 저장 경로 설정 (./chroma_db 폴더에 저장됨)
CHROMA_PATH = "./chroma_db"
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

# 컬렉션 생성 또는 로드 (거리 측정 방식은 코사인 유사도로 설정)
collection = chroma_client.get_or_create_collection(
    name="news_articles_ko",  # 새 모델용 컬렉션 이름
    metadata={"hnsw:space": "cosine"}
)

# Watsonx LLM 설정 (기존 유지)
credentials = {
    "apikey": WATSONX_API_KEY,
    "url": WATSONX_URL
}

llm_model = ModelInference(
    model_id="meta-llama/llama-3-3-70b-instruct",
    credentials=credentials,
    project_id=WATSONX_PROJECT_ID
)

# -------------------------------------------------
# 2. ChromaDB 기반 Embedding 캐시 로직
# -------------------------------------------------
def get_embeddings_with_cache(articles):
    """ChromaDB를 조회하여 캐시된 임베딩이 있으면 가져오고, 없으면 생성 후 저장"""
    article_ids = [str(a.id) for a in articles]
    
    # 1. ChromaDB에서 기존 임베딩 일괄 조회
    existing_data = collection.get(ids=article_ids, include=['embeddings'])
    existing_ids = set(existing_data['ids'])
    
    # 결과 담을 리스트 (순서 보장)
    embeddings = [None] * len(articles)
    id_to_idx = {str(a.id): i for i, a in enumerate(articles)}

    # 기존 데이터 채우기
    for i, aid in enumerate(existing_data['ids']):
        idx = id_to_idx[aid]
        embeddings[idx] = np.array(existing_data['embeddings'][i], dtype=np.float32)

    # 2. 없는 데이터만 임베딩 생성
    to_embed_indices = [i for i, emb in enumerate(embeddings) if emb is None]
    
    if to_embed_indices:
        print(f"      [ChromaDB] {len(to_embed_indices)}건 신규 임베딩 생성 및 저장 중...")
        to_embed_texts = []
        for i in to_embed_indices:
            a = articles[i]
            # 텍스트 정제
            clean_title = re.sub(r'\[.*?\]|\(.*?\)', '', a.title).strip()
            clean_content = (a.contents or '')[:200].replace('\n', ' ')
            to_embed_texts.append(f"제목: {clean_title} 내용: {clean_content}")

        # 신규 임베딩 생성
        new_embs = embed_model.encode(to_embed_texts, normalize_embeddings=True)

        # ChromaDB에 신규 데이터 추가
        collection.add(
            ids=[str(articles[i].id) for i in to_embed_indices],
            embeddings=new_embs.tolist(),
            metadatas=[{"title": articles[i].title} for i in to_embed_indices]
        )

        # 결과 리스트 업데이트
        for i, emb in zip(to_embed_indices, new_embs):
            embeddings[i] = emb

    return np.array(embeddings, dtype="float32")

# -------------------------------------------------
# 3. 보조 로직 (기존 KG 및 LLM 유지)
# -------------------------------------------------
def simple_kg_check(articles):
    if len(articles) < 3: return False
    stopwords = {
    # 기존 단어들
    '오늘', '내일', '속보', '단독', '종합', '기자', '보도', '사진', '포토', '관련', '어제',
    '진행', '개최', '출시', '등록', '확인', '발표', '예정', '위해', '의해', '정치',
    '지난', '이번', '통해', '대한', '업계', '시장', '국내', '글로벌', '의료', '의료계',

    # 추가 제안: 뉴스 일반 (기사 구조 관련)
    '뉴스', '기사', '소식', '정보', '현장', '특징', '정리', '무단', '배포', '금지', '전재', 

    # 추가 제안: 비즈니스/산업 일반 (모든 회사 기사에 겹치는 단어)
    '기업', '업체', '동향', '현황', '사업', '추진', '기대', '전망', '성장', '강화', 
    '목표', '주목', '가속', '본격', '최근', '성공', '결과', '계획', '선정', '확대',

    # 추가 제안: 제약/바이오 특화 노이즈 (사건의 본질이 아닌 단어)
    '바이오', '제약사', '치료', '제품', '기술', '개발', '환자', '사용', '도움', '기능', 
    '효과', '시스템', '도입', '제공', '서비스', '운영', '관리', '인증', '수상', '지원'
}
    def extract_nouns(text):
        # Kiwi로 명사만 추출 (NNG: 일반명사, NNP: 고유명사)
        tokens = kiwi.tokenize(text)
        return set(t.form for t in tokens if t.tag in ['NNG', 'NNP'] and t.form not in stopwords and len(t.form) > 1)

    # 모든 기사 제목에서 명사 추출
    docs_nouns = [extract_nouns(a.title) for a in articles]
    
    # 전체 교집합 확인
    common = docs_nouns[0]
    for d in docs_nouns[1:]:
        common = common.intersection(d)

    return len(common) >= 1

def run_stage2_issue_refine(articles):
    summaries = [f"[{i}] 제목: {a.title}\n요약: {(a.contents or '')[:150]}" for i, a in enumerate(articles[:10])]
    prompt = f"""
역할: 뉴스 통찰력이 뛰어난 베테랑 데스크 기자.
목표: 제공된 기사 목록에서 '완벽하게 동일한 사건'을 다루는 기사들만 골라내어 그룹화하라.

[검증 및 필터링 규칙 - 반드시 준수]
1. **주체(Entity) 일치성:** 기사들의 핵심 주인공(인물, 기업, 기관)이 단 한 명이라도 다르면 절대 같은 이슈가 아닙니다.
   - 오답 예시: 'A배우 별세'와 'B감독 별세'는 '별세'라는 주제만 같을 뿐, 사건은 별개이므로 함께 묶지 마십시오.
2. **사건(Event)의 단일성:** '제약업계 동향'이나 '인사 소식'처럼 여러 사건을 나열한 기사는 이슈로 묶지 말고 제외하십시오.
3. **불순물 제거:** 목록 중 대다수와 다른 주어를 가진 기사가 섞여 있다면, 그 번호는 `valid_indices`에서 반드시 제외하십시오.
4. **최소 요건:** 결과적으로 3개 이상의 기사가 완벽하게 동일한 사건을 다루지 않는다면 `valid_indices: none`을 반환하십시오.

[목록]
{chr(10).join(summaries)}

[출력 형식]
valid_indices: 골라낸 기사 번호들 (예: 0, 1, 3 / 없으면 none)
title: 선택된 기사들을 포괄하는 핵심 요약 제목
"""
    try:
        res = llm_model.generate_text(prompt=prompt, params={"max_new_tokens": 300, "temperature": 0.1})
        parsed = {}
        for line in res.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                parsed[k.strip().lower()] = v.strip()
        raw = parsed.get("valid_indices", "none").lower()
        parsed["valid_ids"] = [] if "none" in raw else [int(x) for x in re.findall(r"\d+", raw)]
        return parsed
    except: return {"valid_ids": []}

# -------------------------------------------------
# 4. 메인 파이프라인 (ChromaDB + HDBSCAN)
# -------------------------------------------------
def run_issue_clustering(db: Session, days=3):
    Base.metadata.create_all(bind=engine)
    since = datetime.now() - timedelta(days=days)
    articles = db.query(Article).filter(Article.time >= since, Article.issue_id.is_(None)).all()
    if len(articles) < 2: return

    # 1. 모든 대상 기사의 임베딩 확보 (ChromaDB 캐시 활용)
    embeddings = get_embeddings_with_cache(articles)

    # 2. 기존 이슈 흡수 (ChromaDB에서 벡터 직접 호출)
    recent_issues = db.query(Issue).filter(Issue.created_at >= since).all()
    for issue in recent_issues:
        sample = db.query(Article).filter(Article.issue_id == issue.id).first()
        if not sample: continue
        
        # ChromaDB에서 기존 이슈의 대표 기사 벡터 가져오기
        res = collection.get(ids=[str(sample.id)], include=['embeddings'])
        embeddings_list = res.get('embeddings')
        if embeddings_list is None or len(embeddings_list) == 0:
            continue
        issue_vec = np.array(res['embeddings'][0]).reshape(1, -1)

        for i, a in enumerate(articles):
            if a.issue_id is not None: continue
            sim = cosine_similarity(embeddings[i].reshape(1, -1), issue_vec)[0][0]
            if sim >= 0.85: a.issue_id = issue.id

    # 3. 신규 클러스터링
    rem = [(i, a) for i, a in enumerate(articles) if a.issue_id is None]
    if len(rem) < 3: # 최소 군집 사이즈 3 고려
        db.commit()
        return

    idxs, rem_articles = zip(*rem)
    rem_embs = normalize(embeddings[list(idxs)])
    
    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=3, 
        min_samples=1, 
        metric="euclidean", 
        cluster_selection_epsilon=0.28
    )
    labels = clusterer.fit_predict(rem_embs)

    for cid in set(labels):
        if cid == -1: continue 
        cluster = [rem_articles[i] for i in np.where(labels == cid)[0]]
        
        if not simple_kg_check(cluster): continue
        res = run_stage2_issue_refine(cluster)
        valid_ids = res.get("valid_ids", [])
        
        if len(valid_ids) < 3: continue 
            
        picked = [cluster[i] for i in valid_ids if i < len(cluster)]
        issue = Issue(title=res.get("title", picked[0].title), created_at=datetime.now())
        db.add(issue)
        db.flush() 
        
        for a in picked: 
            a.issue_id = issue.id
        print(f"✨ [ChromaDB 기반 이슈 생성] {issue.title} (기사 {len(picked)}건)")

    db.commit()
    print("--- [DONE] 클러스터링 및 이슈 업데이트 완료 ---")

# if __name__ == "__main__":
#     db = SessionLocal()
#     try: run_issue_clustering(db)
#     finally: db.close()