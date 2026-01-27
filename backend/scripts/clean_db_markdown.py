import sys
import os
import json # In case we need to parse/dump manually, but SQLAlchemy handles JSON type usually

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from database.engine import SessionLocal
from database import models
from sqlalchemy.orm.attributes import flag_modified

def clean_markdown():
    db = SessionLocal()
    target_ids = [39, 40]
    
    print(f"🧹 Starting cleanup for IDs: {target_ids}")
    
    for news_id in target_ids:
        news = db.query(models.AiGeneratedNews).filter(models.AiGeneratedNews.ai_generated_news_id == news_id).first()
        if not news:
            print(f"   ⚠️ ID {news_id} not found, skipping.")
            continue
            
        if not news.analysis_result:
            print(f"   ⚠️ ID {news_id} has no analysis result.")
            continue
            
        # Get current data
        # Note: SQLAlchemy JSON type returns python dict/list directly
        data = news.analysis_result
        
        if "media_comparison_bullets" in data:
            bullets = data["media_comparison_bullets"]
            clean_bullets = []
            changed = False
            for b in bullets:
                if "**" in b:
                    clean_b = b.replace("**", "")
                    clean_bullets.append(clean_b)
                    changed = True
                else:
                    clean_bullets.append(b)
            
            if changed:
                data["media_comparison_bullets"] = clean_bullets
                # Important: For JSON fields, we must flag modification or re-assign to trigger update
                news.analysis_result = data 
                flag_modified(news, "analysis_result") 
                print(f"   ✅ Cleaned ID {news_id}")
            else:
                print(f"   ℹ️ ID {news_id} needs no changes.")
        else:
             print(f"   ℹ️ ID {news_id} has no bullets.")

    db.commit()
    print("✨ Database cleanup complete!")
    db.close()

if __name__ == "__main__":
    clean_markdown()
