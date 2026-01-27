import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from database.engine import SessionLocal
from database import models

def check():
    db = SessionLocal()
    news = db.query(models.AiGeneratedNews).filter(models.AiGeneratedNews.ai_generated_news_id == 36).first()
    if news:
        print(f"FOUND: News 36 is linked to Cluster {news.cluster_id}")
    else:
        print("NOT FOUND: News 36 does not exist")
    db.close()

if __name__ == "__main__":
    check()
