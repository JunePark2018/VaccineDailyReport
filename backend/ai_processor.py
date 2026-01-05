# ai_processor.py
import os
import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from openai import OpenAI
from models import Article, Issue
from database import SessionLocal
from crud import create_sample_issue

# 🔑 API 키 확인 필수
os.environ["OPENAI_API_KEY"] = "sk-..." 
client = OpenAI()

def process_news_pipeline():
    """
    [MVP 파이프라인]
    1. 분석 안 된 기사 가져오기
    2. 기사별 '입장'과 '근거' 추출 (Extract)
    3. 근거가 비슷한 것끼리 그룹핑 (Cluster)
    4. 그룹별 상세 리포트 작성 (RAG)
    5. DB 저장
    """
    db = SessionLocal()
    print("🧠 [AI] 뉴스 분석 파이프라인 가동...")

    # blablablablabla
    
    create_sample_issue()
    
    print("🧠 [AI] 완료")