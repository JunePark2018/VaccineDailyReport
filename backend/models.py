# models.py
from sqlalchemy import Column, Integer, BigInteger, String, Boolean, Text, ForeignKey, DateTime, JSON # <--- JSON 임포트 필수!
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

# 데이터베이스 모델의 기본 클래스 생성
Base = declarative_base()

# 이슈(Cluster) 테이블: AI가 분석한 주제 그룹
class Issue(Base):
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(Text)
    analysis_result = Column(JSON, nullable=True) 
    
    created_at = Column(DateTime, default=datetime.now)
    articles = relationship("Article", back_populates="issue")

# 기사(Article) 테이블: 수집된 개별 뉴스
class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)                    # 기사 제목
    content = Column(Text)                    # 기사 본문
    url = Column(String, unique=True)         # 기사 링크 (중복 수집 방지)
    publisher = Column(String)                # 언론사 (예: 조선일보, 한겨레)
    image_url = Column(JSON, nullable=True)   # 기사 이미지 리스트
    published_at = Column(DateTime)           # 기사 발행 시간
    
    # 외래키: 이 기사가 어떤 이슈(Issue)에 속하는지 연결
    issue_id = Column(Integer, ForeignKey("issues.id"))
    
    # 관계 설정
    issue = relationship("Issue", back_populates="articles")


# 사용자의 정보가 저장된 클래스
class User(Base):
    __tablename__ = "users"
    
    # Primary Key는 자동으로 NOT NULL, UNIQUE 속성을 가집니다.
    login_id = Column(String(50), primary_key=True)
    
    # user_real_name VARCHAR(50)
    user_real_name = Column(String(50))
    
    # password_hash VARCHAR(255) NOT NULL
    password_hash = Column(String(255), nullable=False)
    
    # email VARCHAR(100)
    email = Column(String(100))
    
    # subscribed_categories JSON ([['정치', 36], ['경제', 27]])
    subscribed_categories = Column(JSON)
    
    # subscribed_keywords JSON ([('삼성전자', , '금리', 'AI'])
    subscribed_keywords = Column(JSON)
    
    # fcm_token VARCHAR(255)
    fcm_token = Column(String(255))
    
    # created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    created_at = Column(DateTime, default=datetime.now)
    
    # view_history JSON ({기사 URL, 기사 조회 시간})
    view_history = Column(JSON)
    
    # preferred_time_range JSON or String
    # 시간 대역을 구조적으로 저장하려면 JSON, 단순 텍스트면 String 사용
    preferred_time_range = Column(JSON) 
    
    # marketing_agree BOOLEAN DEFAULT FALSE
    marketing_agree = Column(Boolean, default=False)
    
    # user_status TINYINT DEFAULT 1 (1:정상, 0:휴면, -1:탈퇴)
    # SQLAlchemy에서는 보통 Integer로 처리하거나 SmallInteger를 사용합니다.
    user_status = Column(Integer, default=1)