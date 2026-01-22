import numpy as np
import re
import os
from dotenv import load_dotenv  # 추가
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
from database.models import Base, News, AiGeneratedNews


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
    name="news_articles_ko", metadata={"hnsw:space": "cosine"}  # 새 모델용 컬렉션 이름
)

# Watsonx LLM 설정 (기존 유지)
credentials = {"apikey": WATSONX_API_KEY, "url": WATSONX_URL}

llm_model = ModelInference(
    model_id="meta-llama/llama-3-3-70b-instruct", credentials=credentials, project_id=WATSONX_PROJECT_ID
)


# -------------------------------------------------
# 2. ChromaDB 기반 Embedding 캐시 로직
# -------------------------------------------------
def get_embeddings_with_cache(articles):
    """ChromaDB를 조회하여 캐시된 임베딩이 있으면 가져오고, 없으면 생성 후 저장"""
    article_ids = [str(a.id) for a in articles]

    # 1. ChromaDB에서 기존 임베딩 일괄 조회
    existing_data = collection.get(ids=article_ids, include=["embeddings"])
    existing_ids = set(existing_data["ids"])

    # 결과 담을 리스트 (순서 보장)
    embeddings = [None] * len(articles)
    id_to_idx = {str(a.id): i for i, a in enumerate(articles)}

    # 기존 데이터 채우기
    for i, aid in enumerate(existing_data["ids"]):
        idx = id_to_idx[aid]
        embeddings[idx] = np.array(existing_data["embeddings"][i], dtype=np.float32)

    # 2. 없는 데이터만 임베딩 생성
    to_embed_indices = [i for i, emb in enumerate(embeddings) if emb is None]

    if to_embed_indices:
        print(f"      [ChromaDB] {len(to_embed_indices)}건 신규 임베딩 생성 및 저장 중...")
        to_embed_texts = []
        for i in to_embed_indices:
            a = articles[i]
            # 텍스트 정제
            clean_title = re.sub(r"\[.*?\]|\(.*?\)", "", a.title).strip()
            clean_content = (a.contents or "")[:200].replace("\n", " ")
            to_embed_texts.append(f"제목: {clean_title} 내용: {clean_content}")

        # 신규 임베딩 생성
        new_embs = embed_model.encode(to_embed_texts, normalize_embeddings=True)

        # ChromaDB에 신규 데이터 추가
        collection.add(
            ids=[str(articles[i].id) for i in to_embed_indices],
            embeddings=new_embs.tolist(),
            metadatas=[{"title": articles[i].title} for i in to_embed_indices],
        )

        # 결과 리스트 업데이트
        for i, emb in zip(to_embed_indices, new_embs):
            embeddings[i] = emb

    return np.array(embeddings, dtype="float32")


# -------------------------------------------------
# 3. 보조 로직 (기존 KG 및 LLM 유지)
# -------------------------------------------------
def simple_kg_check(articles):
    """간단한 KG 기반 클러스터 검증"""
    if len(articles) < 5:  # 3 → 5로 변경
        print(f"    ⚠️ [DEBUG] KG 체크: 기사 수 부족 ({len(articles)}개 < 5)")
        return False

    stopwords = {
        # 기존 단어들
        "오늘",
        "내일",
        "속보",
        "단독",
        "종합",
        "기자",
        "보도",
        "사진",
        "포토",
        "관련",
        "어제",
        "진행",
        "개최",
        "출시",
        "등록",
        "확인",
        "발표",
        "예정",
        "위해",
        "의해",
        "정치",
        "지난",
        "이번",
        "통해",
        "대한",
        "업계",
        "시장",
        "국내",
        "글로벌",
        "의료",
        "의료계",
        # 추가 제안: 뉴스 일반 (기사 구조 관련)
        "뉴스",
        "기사",
        "소식",
        "정보",
        "현장",
        "특징",
        "정리",
        "무단",
        "배포",
        "금지",
        "전재",
        # 추가 제안: 비즈니스/산업 일반 (모든 회사 기사에 겹치는 단어)
        "기업",
        "업체",
        "동향",
        "현황",
        "사업",
        "추진",
        "기대",
        "전망",
        "성장",
        "강화",
        "목표",
        "주목",
        "가속",
        "본격",
        "최근",
        "성공",
        "결과",
        "계획",
        "선정",
        "확대",
        # 추가 제안: 제약/바이오 특화 노이즈 (사건의 본질이 아닌 단어)
        "바이오",
        "제약사",
        "치료",
        "제품",
        "기술",
        "개발",
        "환자",
        "사용",
        "도움",
        "기능",
        "효과",
        "시스템",
        "도입",
        "제공",
        "서비스",
        "운영",
        "관리",
        "인증",
        "수상",
        "지원",
    }

    def extract_nouns(text):
        # Kiwi로 명사만 추출 (NNG: 일반명사, NNP: 고유명사)
        tokens = kiwi.tokenize(text)
        return set(t.form for t in tokens if t.tag in ["NNG", "NNP"] and t.form not in stopwords and len(t.form) > 1)

    # 모든 기사 제목 + 본문(200자)에서 명사 추출
    docs_nouns = [extract_nouns(f"{a.title} {(a.contents or '')[:200]}") for a in articles]

    # 전체 교집합 대신 과반수 조건으로 완화
    from collections import Counter

    all_nouns = []
    for nouns in docs_nouns:
        all_nouns.extend(nouns)

    noun_counts = Counter(all_nouns)
    threshold = len(articles) / 2  # 과반수 (50%)
    common = {noun for noun, count in noun_counts.items() if count >= threshold}

    result = len(common) >= 1
    if result:
        print(f"    ✅ [DEBUG] KG 체크 통과: 과반수 공통 명사 {len(common)}개 - {common}")
    else:
        print(f"    ❌ [DEBUG] KG 체크 실패: 과반수 공통 명사 0개 (threshold={threshold:.1f}개 이상)")
        # 디버깅용: 가장 많이 나타난 명사 3개 출력
        if noun_counts:
            top_nouns = noun_counts.most_common(3)
            print(f"       가장 많이 나타난 명사: {top_nouns}")
    return result


def run_stage2_issue_refine(articles):
    summaries = [f"[{i}] 제목: {a.title}\n요약: {(a.contents or '')[:150]}" for i, a in enumerate(articles[:10])]
    prompt = f"""
역할: 뉴스 통찰력이 뛰어난 베테랑 데스크 기자.
목표: 제공된 기사 목록에서 '같은 이슈'를 다루는 기사들만 골라내어 그룹화하라.

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
    except:
        return {"valid_ids": []}


# -------------------------------------------------
# 4. 메인 파이프라인 (ChromaDB + HDBSCAN)
# -------------------------------------------------
def run_issue_clustering(db: Session, days=3):
    Base.metadata.create_all(bind=engine)
    since = datetime.utcnow() - timedelta(days=days)

    from database import crud

    articles = crud.get_recent_news(db, since)
    print(f"🔍 [DEBUG] 조회된 기사 수: {len(articles) if articles else 0}개")
    if not articles:
        print("⚠️ [DEBUG] 조회된 기사가 없어 클러스터링을 건너뜁니다.")
        return
    if len(articles) < 5:
        print(f"⚠️ [DEBUG] 기사 수 부족 (최소 5개 필요, 현재 {len(articles)}개)")
        return

    # DB 모델에 없는 issue_id 속성을 객체에 강제로 붙이는 대신, 이 딕셔너리를 사용합니다.
    assigned_issues = {}

    # 1. 모든 대상 기사의 임베딩 확보 (ChromaDB 캐시 활용)
    embeddings = get_embeddings_with_cache(articles)
    print(f"📊 [DEBUG] 임베딩 생성 완료: {len(embeddings)}개")

    # 2. 기존 이슈 흡수 (ChromaDB에서 벡터 직접 호출)
    recent_issues = db.query(AiGeneratedNews).filter(AiGeneratedNews.created_at >= since).all()
    print(f"📰 [DEBUG] 기존 이슈 수: {len(recent_issues)}개")
    for issue in recent_issues:
        # [Fix] 이슈 ID로 기사를 찾는 것이 아니라, 이슈와 연결된 클러스터의 기사 중 하나를 대표로 사용
        if not issue.cluster or not issue.cluster.news:
            continue

        # 첫 번째 기사를 대표 벡터로 사용
        sample = issue.cluster.news[0]

        # ChromaDB에서 기존 이슈의 대표 기사 벡터 가져오기
        res = collection.get(ids=[str(sample.id)], include=["embeddings"])
        embeddings_list = res.get("embeddings")
        if embeddings_list is None or len(embeddings_list) == 0:
            continue
        issue_vec = np.array(res["embeddings"][0]).reshape(1, -1)

        # 현재 이슈에 이미 포함된 기사 ID 집합 (중복 연결 방지)
        existing_news_ids = {n.id for n in issue.cluster.news}

        for i, a in enumerate(articles):

            # [Fix] 이미 이 이슈(클러스터)에 포함된 기사라면 유사도 계산 건너뛰기
            if a.id in existing_news_ids:
                # 이미 포함되어 있으므로 그냥 건너뛰거나, 혹은 단순히 넘어감
                continue

            sim = cosine_similarity(embeddings[i].reshape(1, -1), issue_vec)[0][0]
            if sim >= 0.80:  # 보수적 값으로 복원
                assigned_issues[a.id] = issue.id
                print(f"  🔗 [DEBUG] 기사 {a.id}를 기존 이슈 {issue.id}에 연결 (유사도: {sim:.2f})")

    # 3. 신규 클러스터링
    print("클러스터링 시작")
    rem = [(i, a) for i, a in enumerate(articles) if a.id not in assigned_issues]
    print(f"🔗 [DEBUG] 클러스터링 대상 기사: {len(rem)}개")
    if len(rem) < 5:  # 최소 5개로 상향
        print(f"⚠️ [DEBUG] 클러스터링 대상 기사 수 부족 (최소 5개 필요, 현재 {len(rem)}개)")
        db.commit()
        return

    idxs, rem_articles = zip(*rem)
    rem_embs = normalize(embeddings[list(idxs)])

    clusterer = hdbscan.HDBSCAN(min_cluster_size=5, min_samples=1, metric="euclidean", cluster_selection_epsilon=0.28)
    labels = clusterer.fit_predict(rem_embs)
    unique_labels = set(labels)
    cluster_count = len([l for l in unique_labels if l != -1])
    noise_count = sum(1 for l in labels if l == -1)
    print(f"🎯 [DEBUG] HDBSCAN 결과: {cluster_count}개 클러스터, {noise_count}개 노이즈")

    for cid in set(labels):
        if cid == -1:
            continue
        cluster = [rem_articles[i] for i, lbl in enumerate(labels) if lbl == cid]
        print(f"  ├─ 클러스터 {cid}: {len(cluster)}개 기사")

        if not simple_kg_check(cluster):
            print(f"    └─ ❌ 클러스터 {cid} KG 검증 실패")
            continue
        res = run_stage2_issue_refine(cluster)
        valid_ids = res.get("valid_ids", [])
        print(f"    ├─ LLM 검증 결과: {len(valid_ids)}개 유효")

        # if len(valid_ids) < 3:  # 최소 3개 유지
        #     print(f"    └─ ❌ 유효 기사 부족 (최소 3개 필요)")
        #     continue

        # picked = [cluster[i] for i in valid_ids if i < len(cluster)]
        picked = [cluster[i] for i in range(len(cluster))]
        # LLM 유효성 검사가 너무 엄격하여 일단 클러스터 내 기사들을 모두 picked로 설정

        # 4. 이슈 생성 및 DB 반영
        issue = crud.create_ai_news_issue(
            db, title=res.get("title", picked[0].title), article_ids=[a.id for a in picked]
        )
        db.flush()
        print(f"    └─ ✅ 새 이슈 생성: {issue.title}")
        print(f"       (ID: {issue.id}, 기사 {len(picked)}개)")

        # 5. 클러스터 내 기사들에 이슈 ID 연결 (로컬 추적용)
        for a in picked:
            assigned_issues[a.id] = issue.id

    db.commit()
    print("--- [DONE] 클러스터링 및 이슈 업데이트 완료 ---")


# if __name__ == "__main__":
#     db = SessionLocal()
#     try: run_issue_clustering(db)
#     finally: db.close()
