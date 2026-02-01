# VaccineDailyReport/backend/clustering.py

import numpy as np
import re
import os
from dotenv import load_dotenv
import chromadb
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sentence_transformers import SentenceTransformer
import hdbscan
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize
from ibm_watsonx_ai.foundation_models import ModelInference
from kiwipiepy import Kiwi

# DB 관련 임포트 (경로는 프로젝트 구조에 맞게 확인 필요)
from database.engine import SessionLocal, engine
from database.models import Base, News, Report
from database import crud

load_dotenv(override=True)
kiwi = Kiwi()
WATSONX_API_KEY = os.getenv("WATSONX_API_KEY")
WATSONX_PROJECT_ID = os.getenv("WATSONX_PROJECT_ID")
WATSONX_URL = os.getenv("WATSONX_URL")

# -------------------------------------------------
# 1. 초기화 및 ChromaDB 설정
# -------------------------------------------------
# -------------------------------------------------
# 1. 초기화 및 ChromaDB 설정
# -------------------------------------------------
print("--- [AI] 모델 및 ChromaDB 로딩 중... ---")

# [Refactor] vector_store 모듈 사용
from database.vector_store import get_collection, get_embed_model

collection = get_collection()
embed_model = get_embed_model()

credentials = {"apikey": WATSONX_API_KEY, "url": WATSONX_URL}
llm_model = ModelInference(
    model_id="meta-llama/llama-3-3-70b-instruct", credentials=credentials, project_id=WATSONX_PROJECT_ID
)


# -------------------------------------------------
# 2. ChromaDB 기반 Embedding 캐시 로직 (팀원 버전 채택)
# -------------------------------------------------
def get_embeddings_with_cache(articles):
    """
    기사 목록의 임베딩을 ChromaDB에서 조회하고, 없으면 생성하여 저장합니다.
    """
    article_ids = [str(a.news_id) for a in articles]

    # 1. ChromaDB 조회
    existing_data = collection.get(ids=article_ids, include=["embeddings"])
    id_to_embedding = {
        aid: np.array(emb, dtype=np.float32) for aid, emb in zip(existing_data["ids"], existing_data["embeddings"])
    }

    # 2. 없는 데이터 확인 및 생성
    to_embed_indices = [i for i, a in enumerate(articles) if str(a.news_id) not in id_to_embedding]

    if to_embed_indices:
        print(f"    [ChromaDB] {len(to_embed_indices)}건 신규 임베딩 생성 중...")
        to_embed_texts = []
        for i in to_embed_indices:
            a = articles[i]
            # 제목과 본문 앞부분을 결합하여 임베딩 품질 향상
            clean_title = re.sub(r"\[.*?\]|\(.*?\)", "", a.title).strip()
            clean_content = (a.contents or "")[:200].replace("\n", " ")
            to_embed_texts.append(f"제목: {clean_title} 내용: {clean_content}")

        new_embs = embed_model.encode(to_embed_texts, normalize_embeddings=True)

        # ChromaDB 저장
        new_ids = [str(articles[i].news_id) for i in to_embed_indices]
        collection.add(
            ids=new_ids,
            embeddings=new_embs.tolist(),
            metadatas=[{"title": articles[i].title} for i in to_embed_indices],
        )

        for aid, emb in zip(new_ids, new_embs):
            id_to_embedding[aid] = emb

    # 3. 입력 순서대로 정렬하여 반환
    return np.array([id_to_embedding[str(a.news_id)] for a in articles], dtype=np.float32)


# -------------------------------------------------
# 3. 보조 로직 (KG 체크 및 LLM 검증)
# -------------------------------------------------
def simple_kg_check(articles):
    """
    최소한의 공통 명사가 있는지 확인하여 엉뚱한 기사가 섞이는 것을 방지
    """
    if len(articles) < 3:
        return False

    stopwords = {
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
        "기본",
    }

    def extract_nouns(text):
        tokens = kiwi.tokenize(text)
        return set(t.form for t in tokens if t.tag in ["NNG", "NNP"] and t.form not in stopwords and len(t.form) > 1)

    docs_nouns = [extract_nouns(a.title) for a in articles]

    # 첫 번째 기사의 명사들을 기준으로 교집합 수행
    common = docs_nouns[0]
    for d in docs_nouns[1:]:
        common = common.intersection(d)

    # 공통 핵심어가 1개 이상이면 통과
    return len(common) >= 1


def run_stage2_issue_refine(articles):
    """
    LLM을 사용하여 실제로 동일한 이슈인지 최종 검증
    """
    summaries = [f"[{i}] 제목: {a.title}\n요약: {(a.contents or '')[:150]}" for i, a in enumerate(articles[:10])]

    prompt = f"""
역할: 뉴스 통찰력이 뛰어난 베테랑 데스크 기자.
목표: 제공된 기사 목록에서 '완벽하게 동일한 사건'을 다루는 기사들만 골라내어 그룹화하라.

[검증 및 필터링 규칙 - 반드시 준수]
1. **주체(Entity) 일치성:** 기사들의 핵심 주인공(인물, 기업, 기관)이 단 한 명이라도 다르면 절대 같은 이슈가 아닙니다.
2. **사건(Event)의 단일성:** '제약업계 동향'처럼 여러 사건을 나열한 기사는 제외하십시오.
3. **불순물 제거:** 목록 중 대다수와 다른 주어를 가진 기사가 있다면 제외하십시오.
4. **최소 요건:** 결과적으로 3개 이상의 기사가 완벽하게 동일한 사건을 다루지 않는다면 `valid_indices: none`을 반환하십시오.

[목록]
{chr(10).join(summaries)}

[출력 형식]
valid_indices: 골라낸 기사 번호들 (예: 0, 1, 3 / 없으면 none)
title: 이 이슈를 관통하는 핵심 제목 (하나의 문장으로 작성)
"""

    try:
        res = llm_model.generate_text(prompt=prompt, params={"max_new_tokens": 500, "temperature": 0.1})

        parsed = {}
        for line in res.splitlines():
            if "valid_indices" in line.lower() and ":" in line:
                raw_val = line.split(":", 1)[1].strip().lower()
                parsed["valid_ids"] = [] if "none" in raw_val else [int(x) for x in re.findall(r"\d+", raw_val)]
            if "title" in line.lower() and ":" in line:
                parsed["title"] = line.split(":", 1)[1].strip()

        return parsed
    except Exception as e:
        print(f"LLM 검증 오류: {e}")
        return {"valid_ids": []}


# -------------------------------------------------
# 4. 메인 파이프라인
# -------------------------------------------------
def run_issue_clustering(db: Session, days=3):
    Base.metadata.create_all(bind=engine)
    since = datetime.now() - timedelta(days=days)

    # 1. 기사 조회
    articles = crud.get_recent_news(db, since)
    articles = [a for a in articles if not a.clusters]
    print(f"🔍 [DEBUG] 조회된 기사 수: {len(articles) if articles else 0}개")

    if len(articles) < 3:
        print("⚠️ 기사가 부족하여 클러스터링을 종료합니다.")
        return

    # 런타임 처리를 위한 issue_id 초기화 (DB에는 없는 필드)
    for a in articles:
        a.issue_id = None

    # 2. 임베딩 확보
    embeddings = get_embeddings_with_cache(articles)

    # 3. [복구됨] 기존 이슈에 새 기사 병합 (Absorption)
    #    - 기존 이슈와 유사도가 매우 높으면(0.85 이상) 해당 이슈로 편입시킵니다.
    print("🔄 [DEBUG] 기존 이슈와의 병합 검사 시작...")
    recent_issues = db.query(Report).filter(Report.created_at >= since).all()

    for issue in recent_issues:
        # 이슈에 연결된 기사 중 하나를 대표로 선정 (Cluster -> News 관계 활용)
        if not issue.cluster or not issue.cluster.news:
            continue

        sample_news = issue.cluster.news[0]

        # 대표 기사의 임베딩 가져오기 (ChromaDB 활용)
        res = collection.get(ids=[str(sample_news.news_id)], include=["embeddings"])
        if len(res["embeddings"]) == 0:
            continue

        issue_vec = np.array(res["embeddings"][0]).reshape(1, -1)

        for i, a in enumerate(articles):
            # 이미 이슈가 할당된 기사는 패스
            if getattr(a, "issue_id", None) is not None:
                continue

            raw_sim = cosine_similarity(embeddings[i].reshape(1, -1), issue_vec)[0][0]
            sim = float(raw_sim)
            if sim >= 0.85:
                a.issue_id = issue.report_id
                # DB 연결: Cluster에 뉴스 추가
                crud.add_news_to_cluster(db, cluster_id=issue.cluster_id, news_id=a.news_id)
                print(f"  🔗 [병합] '{a.title}' -> 기존 이슈 '{issue.title}' (유사도: {sim:.2f})")

    # 4. 신규 클러스터링 (HDBSCAN)
    print("🚀 [DEBUG] 신규 클러스터링 시작...")

    # 이슈가 할당되지 않은 기사들만 필터링
    rem = [(i, a) for i, a in enumerate(articles) if getattr(a, "issue_id", None) is None]

    if len(rem) < 3:
        print("⚠️ 남은 기사가 부족하여 신규 클러스터링을 생략합니다.")
        db.commit()
        return

    idxs, rem_articles = zip(*rem)
    rem_embs = normalize(embeddings[list(idxs)])

    # min_cluster_size=3 (팀원 코드 반영: 소규모 데이터 대응)
    clusterer = hdbscan.HDBSCAN(min_cluster_size=3, min_samples=1, metric="euclidean", cluster_selection_epsilon=0.33)
    labels = clusterer.fit_predict(rem_embs)

    for cid in set(labels):
        if cid == -1:  # 노이즈
            continue

        # 현재 클러스터에 속한 기사들
        cluster_indices = np.where(labels == cid)[0]
        cluster = [rem_articles[i] for i in cluster_indices]

        # 1차 검증: KG Check
        if not simple_kg_check(cluster):
            continue

        # 2차 검증: LLM Refine
        res = run_stage2_issue_refine(cluster)
        valid_ids = res.get("valid_ids", [])

        if len(valid_ids) < 3:
            continue

        picked = [cluster[i] for i in valid_ids if i < len(cluster)]
        final_title = res.get("title", picked[0].title)

        # 5. 이슈 생성 및 DB 저장
        issue = crud.create_report(db, title=final_title, article_ids=[a.news_id for a in picked])

        # 런타임 객체에 issue_id 마킹 (중복 처리 방지용)
        for a in picked:
            a.issue_id = issue.report_id

        print(f"✨ [이슈 생성 완료] {final_title} (기사 {len(picked)}건)")

    db.commit()
    print("--- [DONE] 모든 작업 완료 ---")
