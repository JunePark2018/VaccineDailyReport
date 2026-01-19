import sys
import os

# 현재 디렉토리(backend)를 sys.path에 추가하여 모듈 import 가능하게 함
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from database.engine import SessionLocal, engine
from database.models import Base
from database import crud, models
from sqlalchemy.orm import Session
from datetime import datetime


def test_crud_procedures():
    # 1. DB 초기화 (테스트용으로 테이블 다시 생성)
    # 실제 운영 DB라면 절대 Drop 하면 안되지만, 개발/테스트 중이므로 리셋
    print(">>> (Re)Creating tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # 2. User Create Test
        print("\n>>> Testing create_user...")
        user_data = {
            "login_id": "test_user_01",
            "password_hash": "hashed_pw_123",
            "user_real_name": "홍길동",
            "subscribed_categories": ["정치", "경제"],
            "subscribed_keywords": ["의대증원", "삼성전자"],
        }
        user = crud.create_user(db, user_data)
        assert user is not None
        assert user.login_id == "test_user_01"
        # 관계 설정 확인
        assert len(user.subscribed_categories) == 2
        assert len(user.subscribed_keywords) == 2
        print(
            f"User created: {user.login_id} with {len(user.subscribed_categories)} cats & {len(user.subscribed_keywords)} kwds"
        )

        # 3. News Create Test
        print("\n>>> Testing create_news...")
        news_data = {
            "title": "의대 증원 2000명 확정",
            "contents": "정부는 의대 정원을 2000명 늘리기로...",
            "url": "http://news.test/1",
            "company_name": "테스트일보",
            "published_at": "2024-05-20 10:00:00",
            "cluster_title": "의료 개혁 논란",
        }
        news = crud.create_news(db, news_data)
        assert news is not None
        assert news.company.name == "테스트일보"
        assert len(news.clusters) == 1
        assert news.clusters[0].title == "의료 개혁 논란"
        print(f"News created: {news.title} from {news.company.name}")

        # 4. AiGeneratedNews Create Test
        print("\n>>> Testing create_ai_generated_news...")
        cluster_id = news.clusters[0].id
        ai_data = {
            "title": "AI 요약: 의료 개혁",
            "contents": "양측의 입장이 팽팽하다.",
            "analysis_result": {"positive": 30, "negative": 70},
            "keywords": ["의료", "파업"],
        }
        ai_news = crud.create_ai_generated_news(db, ai_data, cluster_id=cluster_id)
        assert ai_news is not None
        assert ai_news.cluster_id == cluster_id
        print(f"AI News created: {ai_news.title} (Cluster ID: {ai_news.cluster_id})")

        # 5. User Interest Increase Test
        print("\n>>> Testing increase_user_interest...")
        # (1) 카테고리 '정치' 읽음
        crud.increase_user_interest(db, "test_user_01", category="정치")
        # (2) 키워드 '의대증원' 읽음
        crud.increase_user_interest(db, "test_user_01", keywords=["의대증원"])

        # 확인
        stat_cat = db.query(models.UserCategoryReadStat).filter_by(user_id=user.id).first()
        stat_kwd = db.query(models.UserKeywordReadStat).filter_by(user_id=user.id).first()

        print(f"Stats -> Category '{stat_cat.category_id}' count: {stat_cat.read_count}")
        print(f"Stats -> Keyword '{stat_kwd.keyword_id}' count: {stat_kwd.read_count}")

        assert stat_cat.read_count == 1
        assert stat_kwd.read_count == 1

        # 한번 더 증가
        crud.increase_user_interest(db, "test_user_01", category="정치")
        db.refresh(stat_cat)
        assert stat_cat.read_count == 2
        print(f"Stats updated -> Category count: {stat_cat.read_count}")

    except Exception as e:
        print(f"❌ Test Failed: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    test_crud_procedures()
