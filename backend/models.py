# models.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON # <--- JSON 임포트 필수!
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