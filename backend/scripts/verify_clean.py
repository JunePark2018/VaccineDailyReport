import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from database.engine import SessionLocal
from database import models

def verify():
    db = SessionLocal()
    ids = [39, 40]
    print("🔍 Verification Results:")
    for nid in ids:
        news = db.query(models.AiGeneratedNews).filter(models.AiGeneratedNews.ai_generated_news_id == nid).first()
        if news and news.analysis_result:
            bullets = news.analysis_result.get("media_comparison_bullets", [])
            has_markdown = any("**" in b for b in bullets)
            status = "❌ FAIL (Has **)" if has_markdown else "✅ PASS (Clean)"
            print(f"ID {nid}: {status}")
            # print(f"   {bullets}") 
        else:
            print(f"ID {nid}: Not Found or No Result")
    db.close()

if __name__ == "__main__":
    verify()
