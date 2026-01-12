# crud.py
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from database import SessionLocal
from models import Article, Issue, User
from datetime import datetime
from sqlalchemy.exc import IntegrityError

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
    time_limit = datetime.now() - timedelta(hours=24)
    existing_title = db.query(Article).filter(
        Article.title == news_data["title"],
        Article.company_name == news_data["company_name"],
        Article.time >= time_limit
    ).first()
    
    if existing_title:
        print(f"   [Skip] 중복 제목(최근 24시간 이내) 건너뜀: {news_data['title'][:20]}...")
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
        contents=news_data["contents"],
        category=news_data["category"],
        url=news_data["url"],
        company_name=news_data["company_name"],
        img_urls=news_data["img_urls"],
        time=pub_date,
        author=news_data["author"]
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
            contents="AI가 쓴 테스트용 기사입니다.",
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

# 유저 데이터 백엔드에 저장하는 함수    
def create_user(db: Session, user_data: dict):
    """
    딕셔너리 형태의 데이터를 받아 DB에 저장합니다.
    이미 존재하는 login_id라면 저장을 실패하고 None을 반환합니다.
    """
    raw_cats = user_data.get("subscribed_categories")
    raw_kwds = user_data.get("subscribed_keywords")

    # 카테고리가 리스트면 딕셔너리로 변환, 아니면 그대로 사용(또는 빈 딕셔너리)
    if not raw_cats:
        raw_cats = []

    # 키워드가 리스트면 딕셔너리로 변환
    if not raw_kwds:
        raw_kwds = []
    
    # 모델 인스턴스 생성
    new_user = User(
        login_id=user_data["login_id"],  # 필수 (PK)
        password_hash=user_data["password_hash"], # 필수
        
        # 아래는 선택 항목 (.get으로 없으면 None 처리)
        user_real_name=user_data.get("user_real_name"),
        email=user_data.get("email"),        
        age_range=user_data.get("age_range"),
        gender=user_data.get("gender"),
        subscribed_categories=raw_cats,
        subscribed_keywords=raw_kwds,
        marketing_agree=user_data.get("marketing_agree", False)
    )

    db.add(new_user)
    db.commit()      # DB에 반영
    db.refresh(new_user) # 저장된 데이터(default 값 등)를 다시 로드
    print(f"[성공] 사용자 '{new_user.login_id}' 생성 완료!")
    return new_user
    
#유저 데이터 백엔드에서 불러오는 함수    
def get_user(db: Session, login_id: str):
    """
    login_id를 기준으로 사용자 정보를 가져옵니다.
    Primary Key로 검색하므로 속도가 매우 빠릅니다.
    """
    return db.query(User).filter(User.login_id == login_id).first()

# 기사를 봤을 때 카운트가 증가하는 함수
def increase_user_interest(db: Session, login_id: str, category: str, keywords: List[str] = None):
    user = db.query(User).filter(User.login_id == login_id).first()
    if not user:
        return None
    
    # 1. 카테고리 카운트 증가
    current_cats = user.read_categories or {} # 기존 값 가져오기
    # 가져온 값이 딕셔너리가 아니라면(혹시 모를 에러 방지) 딕셔너리로 변환
    if isinstance(current_cats, list): 
        current_cats = {c: 1 for c in current_cats}
        
    current_count = current_cats.get(category, 0) # 기존 점수 확인
    current_cats[category] = current_count + 1    # 점수 +1
    user.read_categories = dict(current_cats) # [중요] 재할당해야 DB가 인식함
    
    flag_modified(user, "read_categories")

    # 2. 키워드 카운트 증가 (키워드가 있을 경우에만)
    if keywords:
        current_kwds = user.read_keywords or {}
        if isinstance(current_kwds, list):
            current_kwds = {k: 1 for k in current_kwds}
            
        for keyword in keywords:
            kwd_count = current_kwds.get(keyword, 0)
            current_kwds[keyword] = kwd_count + 1
            user.read_keywords = dict(current_kwds)
    
        flag_modified(user, "read_keywords")

    db.commit()
    return user