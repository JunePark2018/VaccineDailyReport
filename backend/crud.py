# crud.py
from sqlalchemy.orm import Session
from models import Article
from datetime import datetime

def create_article(db: Session, news_data: dict):
    """
    크롤링한 딕셔너리 데이터를 받아서 DB에 저장하는 함수
    (이미 저장된 URL이면 건너뜁니다)
    """
    # 1. 중복 검사: 똑같은 링크(URL)가 이미 있는지 확인
    existing_article = db.query(Article).filter(Article.url == news_data["url"]).first()
    if existing_article:
        print(f"  [Skip] 이미 저장된 기사입니다: {news_data['title']}")
        return None

    # 2. 날짜 변환 (문자열 -> datetime 객체)
    # 네이버 뉴스 날짜 형식: "2024-05-20 14:00:01"
    try:
        if news_data["published_at"]:
            pub_date = datetime.strptime(news_data["published_at"], "%Y-%m-%d %H:%M:%S")
        else:
            pub_date = datetime.now() # 날짜 없으면 현재 시간
    except Exception:
        pub_date = datetime.now() # 변환 에러나도 일단 현재 시간으로

    # 3. 데이터 객체 생성
    new_article = Article(
        title=news_data["title"],
        content=news_data["content"],
        url=news_data["url"],
        publisher=news_data["publisher"],
        image_url=news_data["image_url"],
        published_at=pub_date,
        # issue_id는 나중에 AI가 클러스터링할 때 채워줍니다. 지금은 비워둡니다(NULL).
    )

    # 4. DB에 추가 및 저장
    db.add(new_article)
    db.commit()
    db.refresh(new_article)
    
    print(f"  [Save] 저장 완료: {news_data['title']}")
    return new_article

def is_url_exists(db: Session, url: str) -> bool:
    # 데이터 전체를 가져오지 않고, 존재하는지만 체크 (속도 최적화)
    return db.query(Article.id).filter(Article.url == url).first() is not None