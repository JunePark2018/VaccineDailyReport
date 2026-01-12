import numpy as np
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sklearn.cluster import DBSCAN
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# 기존 파일들에서 필요한 객체 임포트
from database import SessionLocal, engine
from models import Base, Article, Issue

# 1. 모델 로드 (서버 기동 시 한 번만)
print("--- [AI] Ko-sroberta 모델 로딩 중... ---")
model = SentenceTransformer('jhgan/ko-sroberta-multitask')

def run_issue_clustering(db: Session, days: int = 1, eps: float = 0.5):
    # [Step 1] 테이블 생성 확인 (없으면 생성)
    Base.metadata.create_all(bind=engine)

    # [Step 2] 최근 n일간의 이슈가 배정되지 않은 기사들 가져오기
    time_threshold = datetime.now() - timedelta(days=days)
    articles = db.query(Article).filter(
        Article.time >= time_threshold,
        Article.issue_id == None  # 아직 분류되지 않은 기사 위주로 처리
    ).all()

    if len(articles) < 2:
        print(f"--- [Skip] 분류할 기사가 부족합니다. (현재: {len(articles)}개) ---")
        return

    # [Step 3] 텍스트 가공 및 임베딩 생성
    input_texts = [f"{a.title} {a.contents[:100]}" for a in articles]
    embeddings = model.encode(input_texts)

    # [Step 4] DBSCAN 군집화
    # metric='cosine'은 문장 유사도 분석의 표준입니다.
    dbscan = DBSCAN(eps=eps, min_samples=2, metric='cosine')
    clusters = dbscan.fit_predict(embeddings)

    # [Step 5] 군집별 결과 처리
    unique_clusters = set(clusters)
    print(f"--- [AI] 분석 완료: {len(unique_clusters) - (1 if -1 in unique_clusters else 0)}개 이슈 발견 ---")

    for cluster_id in unique_clusters:
        if cluster_id == -1: # 어떤 군집에도 속하지 못한 기사
            continue

        # 해당 군집에 속한 기사 인덱스 추출
        indices = [i for i, val in enumerate(clusters) if val == cluster_id]
        cluster_embeddings = embeddings[indices]
        cluster_articles = [articles[i] for i in indices]

        # [Centroid 로직] 중심점 계산하여 대표 기사 선정
        centroid = np.mean(cluster_embeddings, axis=0)
        sims = cosine_similarity([centroid], cluster_embeddings)[0]
        rep_idx = np.argmax(sims)
        topic_article = cluster_articles[rep_idx]

        # [Step 6] DB 저장: Issue 생성 및 Article 연결
        try:
            # 1. 부모 테이블(Issue)에 새로운 이슈 행 생성
            new_issue = Issue(
                title=topic_article.title, # 대표 기사 제목을 이슈 제목으로 사용
                contents=f"{len(cluster_articles)}개의 기사가 포함된 이슈입니다.",
                analysis_result={"status": "clustered", "main_company": topic_article.company_name},
                created_at=datetime.now()
            )
            db.add(new_issue)
            db.flush() # new_issue.id를 미리 할당받음

            # 2. 자식 테이블(Article)들에 방금 만든 Issue ID 연결
            for a in cluster_articles:
                a.issue_id = new_issue.id
            
            print(f"   > 이슈 생성 완료: {new_issue.title} ({len(cluster_articles)}건)")
            
        except Exception as e:
            print(f"   > 이슈 저장 중 오류: {e}")
            db.rollback()

    db.commit()
    print("--- [Success] 모든 군집 결과가 DB에 반영되었습니다. ---")

if __name__ == "__main__":
    db = SessionLocal()
    try:
        # eps=0.5: 적절한 묶음 수준. 더 깐깐하게 하려면 0.45로 조정하세요.
        run_issue_clustering(db, eps=0.5)
    finally:
        db.close()