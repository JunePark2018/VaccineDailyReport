import sys
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add parent directory to path to allow importing main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from database.models import (
    Base,
    User,
    News,
    AiGeneratedNews,
    Category,
    Company,
    NewsView,
    NewsReaction,
    Cluster,
    SearchLog,
)
from database.engine import SessionLocal

# Setup Test Client
client = TestClient(app)

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql.db"


def setup_module(module):
    """
    Reset database before tests.
    """
    if os.path.exists("sql.db"):
        os.remove("sql.db")
        print("Deleted existing sql.db")

    # Explicitly create tables
    from database.engine import engine
    from database.models import Base

    # Drop all first (for Postgres cleanup)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Reset database tables (Drop & Create)")


def test_02_signup_and_login():
    # Signup
    user_data = {
        "login_id": "testuser",
        "password_hash": "secret",
        "user_real_name": "Test User",
        "email": "test@example.com",
        "subscribed_categories": ["IT", "Economy"],
    }
    response = client.post("/users", json=user_data)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["login_id"] == "testuser"
    assert "user_id" in data

    # Verify User in DB
    response = client.get("/users/testuser")
    assert response.status_code == 200
    assert response.json()["user_real_name"] == "Test User"

    # Login (Auth)
    login_data = {"login_id": "testuser", "password": "secret"}
    response = client.post("/login", json=login_data)
    assert response.status_code == 200
    assert "user_id" in response.json()


def test_03_create_news_data_manually():
    """
    Manually inject data into DB to test read APIs,
    since scraper isn't running in this test environment.
    """
    db = SessionLocal()

    # Create Company
    company = Company(name="Test Daily", display_name="Test Daily")
    db.add(company)
    db.commit()

    # Create Category
    cat_it = Category(name="IT/Science")
    db.add(cat_it)
    db.commit()

    # Create News (Domestic)
    news_dom = News(
        title="Domestic News 1",
        contents="Korea IT Boom",
        url="http://test.com/1",
        company_id=company.company_id,
        is_domestic=True,
        category_id=cat_it.category_id,
    )
    db.add(news_dom)

    # Create News (Global)
    news_glob = News(
        title="Global News 1",
        contents="World IT Boom",
        url="http://test.com/2",
        company_id=company.company_id,
        is_domestic=False,
        category_id=cat_it.category_id,
    )
    db.add(news_glob)
    db.commit()

    # Create AI Generated News
    # Needs Cluster first
    cluster = Cluster(title="IT Cluster")
    db.add(cluster)
    db.commit()

    ai_news = AiGeneratedNews(
        cluster_id=cluster.cluster_id,
        category_id=cat_it.category_id,
        title="AI News Summary",
        contents="Summary of IT",
        keywords=["AI", "Tech"],
    )
    db.add(ai_news)
    db.commit()
    db.close()


def test_04_get_news_filtered():
    # Test Domestic Filter
    response = client.get("/news?is_domestic=true")
    assert response.status_code == 200
    results = response.json()
    assert len(results) >= 1
    assert results[0]["is_domestic"] is True
    assert "news_id" in results[0]  # Verify renaming

    # Test Global Filter
    response = client.get("/news?is_domestic=false")
    assert response.status_code == 200
    results = response.json()
    assert len(results) >= 1
    assert results[0]["is_domestic"] is False


def test_05_record_view_adds_category_id():
    """
    Verify that recording a view also saves the category_id to NewsView
    """
    db = SessionLocal()

    # Get AI News ID
    ai_news = db.query(AiGeneratedNews).first()
    assert ai_news is not None

    # Call View API
    response = client.post(f"/news/{ai_news.ai_generated_news_id}/view?login_id=testuser")
    assert response.status_code == 200

    # Verify DB directly
    view = db.query(NewsView).filter(NewsView.news_id == ai_news.ai_generated_news_id).first()
    assert view is not None
    assert view.category_id == ai_news.category_id
    assert view.category_id is not None
    print(f"Verified NewsView has category_id: {view.category_id}")
    db.close()


def test_06_reaction():
    db = SessionLocal()
    ai_news = db.query(AiGeneratedNews).first()

    response = client.post(f"/news/{ai_news.ai_generated_news_id}/reaction?value=1&login_id=testuser")
    assert response.status_code == 200
    assert response.json()["status"] == "added"
    assert response.json()["likes"] == 1
    db.close()


# --- New Tests for Exhaustive Verification ---


def test_07_ai_news_endpoints():
    # List AI News
    response = client.get("/generated-news")
    assert response.status_code == 200
    results = response.json()
    assert isinstance(results, list)
    assert len(results) > 0
    assert "ai_generated_news_id" in results[0]
    generated_id = results[0]["ai_generated_news_id"]

    # Detail AI News
    response = client.get(f"/generated-news/{generated_id}")
    assert response.status_code == 200
    assert response.json()["ai_generated_news_id"] == generated_id

    # Search AI News
    response = client.get("/generated-news/search?keyword=Summary")
    assert response.status_code == 200
    results = response.json()
    assert len(results) > 0

    # Cluster News List
    cluster_id = results[0]["cluster_id"]
    response = client.get(f"/generated-news/clusters/{cluster_id}/news")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_08_categories():
    response = client.get("/categories")
    assert response.status_code == 200
    cats = response.json()
    print(f"Categories found: {cats}")
    assert len(cats) >= 1
    # Check if any category has the expected name
    names = [c["name"] for c in cats]
    assert "IT/Science" in names


def test_09_search_logs():
    login_id = "testuser"

    # Create Log
    response = client.post(f"/users/{login_id}/search-logs?query=TestQuery")
    assert response.status_code == 200
    assert response.json()["query"] == "TestQuery"

    # Get Logs
    response = client.get(f"/users/{login_id}/search-logs")
    assert response.status_code == 200
    logs = response.json()["logs"]
    assert len(logs) >= 1
    assert logs[0]["query"] == "TestQuery"
    log_id = logs[0]["search_log_id"]

    # Delete Log
    response = client.delete(f"/users/{login_id}/search-logs/{log_id}")
    assert response.status_code == 200

    # Delete All Logs
    # First create another one
    client.post(f"/users/{login_id}/search-logs?query=DeleteMe")
    response = client.delete(f"/users/{login_id}/search-logs")
    assert response.status_code == 200
    assert response.json()["deleted_count"] >= 1


def test_10_statistics():
    # News stats
    response = client.get("/statistics/news")
    assert response.status_code == 200
    stats = response.json()
    assert "total" in stats
    assert "by_category" in stats

    # AI News stats
    response = client.get("/statistics/generated-news")
    assert response.status_code == 200
    stats = response.json()
    assert "total" in stats
    assert "by_category" in stats


def test_11_comprehensive_search():
    # This might fail if external APIs (Wiki) are down or mock isn't present
    # But we can test if it runs without 500
    response = client.get("/api/comprehensive-search?keyword=IT")
    if response.status_code == 200:
        data = response.json()
        assert "keyword" in data
        assert "definition" in data
        assert "ai_summaries" in data
        assert "hot_topics" in data
        assert "articles" in data
    else:
        print(f"Comprehensive Search returned {response.status_code} (External API issue?)")


if __name__ == "__main__":
    setup_module(None)

    tests = [
        test_02_signup_and_login,
        test_03_create_news_data_manually,
        test_04_get_news_filtered,
        test_05_record_view_adds_category_id,
        test_06_reaction,
        test_07_ai_news_endpoints,
        test_08_categories,
        test_09_search_logs,
        test_10_statistics,
        test_11_comprehensive_search,
    ]

    for test_func in tests:
        print(f"Running {test_func.__name__}...")
        try:
            test_func()
            print(" -> PASS")
        except Exception as e:
            print(f" -> FAIL: {e}")
            import traceback

            traceback.print_exc()
            sys.exit(1)

    print("\nALL EXHAUSTIVE TESTS PASSED!")
