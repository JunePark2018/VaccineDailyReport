# crud.py
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Article, Issue
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
        content=news_data["contents"],
        url=news_data["url"],
        publisher=news_data["company_name"],
        image_url=news_data["img_url"],
        published_at=pub_date,
        # issue_id는 나중에 AI가 클러스터링할 때 채워줍니다. 지금은 비워둡니다(NULL).
    )

    # 4. DB에 추가 및 저장
    db.add(new_article)
    db.commit()
    db.refresh(new_article)
    
    print(f"[저장] {news_data['company_name']} - {news_data['title']}")
    return new_article

def is_url_exists(db: Session, url: str) -> bool:
    # 데이터 전체를 가져오지 않고, 존재하는지만 체크 (속도 최적화)
    return db.query(Article.id).filter(Article.url == url).first() is not None

def create_sample_issue():
    # 1. DB 세션 열기
    db = SessionLocal()

    try:
        # 2. 저장할 데이터 준비
        # analysis_result는 JSON 컬럼이므로, 파이썬 딕셔너리나 리스트를 그대로 넣으면 됩니다.
        ai_data = [
            {
                "label": "찬성", 
                "summary": "정부의 의료 개혁 의지 지지", 
                "media": ["조선일보", "중앙일보"]
            },
            {
                "label": "반대", 
                "summary": "준비 없는 증원은 교육 질 저하", 
                "media": ["한겨레", "경향신문"]
            }
        ]

        # 3. Issue 객체 생성 (id와 created_at은 자동 생성되므로 안 넣어도 됨)
        new_issue = Issue(
            title="의대 증원 2천명 확정, 의료계 반발 심화",
            content="AI가 쓴 테스트용 기사입니다.",
            analysis_result=ai_data
        )

        # 4. DB에 저장 절차
        db.add(new_issue)      # (1) 세션(장바구니)에 담기
        db.commit()            # (2) 실제 DB에 저장 (이 시점에 ID가 생김)
        db.refresh(new_issue)  # (3) DB에서 방금 만든 ID와 시간을 다시 객체로 불러오기

        print(f"✅ 저장 성공! ID: {new_issue.id}")
        print(f"📅 생성 시간: {new_issue.created_at}")
        print(f"📊 분석 데이터: {new_issue.analysis_result}")

    except Exception as e:
        print(f"❌ 에러 발생: {e}")
        db.rollback() # 에러 나면 저장 취소
    finally:
        db.close()    # 세션 닫기 (필수)