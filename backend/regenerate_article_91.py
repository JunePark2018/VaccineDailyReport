import asyncio
import os
import sys
import json
from sqlalchemy.orm import Session
from database.engine import SessionLocal
from database.models import Report
from ai_report_generator import generate_balanced_article
from dotenv import load_dotenv

# Add current directory to path so imports work
sys.path.append(os.getcwd())

load_dotenv(override=True)
MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

def regenerate_article_91():
    db = SessionLocal()
    try:
        # 1. Fetch Report ID 91
        print("[INFO] Fetching report ID 91...")
        report = db.query(Report).filter(Report.report_id == 91).first()
        
        if not report:
            print("[ERROR] Report 91 not found.")
            return

        print(f"[INFO] Found Report: {report.title}")
        
        cluster = report.cluster
        if not cluster or not cluster.news:
            print("[ERROR] No cluster or news associated with this report.")
            return
            
        articles = cluster.news
        print(f"[INFO] Found {len(articles)} articles in cluster.")
        
        # 2. Prepare Data for Generator
        # generate_balanced_article expects list of dicts with keys: company_name, title, contents
        news_data = []
        for art in articles:
            news_data.append({
                "company_name": art.company_name,
                "title": art.title,
                "contents": art.contents
            })
            
        # 3. Generate New Content
        print("[INFO] Regenerating article content...")
        # Cluster topic can be inferred or just passed as generic if not available in DB.
        # Report category name might give a hint, or just use cluster title.
        topic = cluster.title or "General News"
        
        result = generate_balanced_article(MODEL_NAME, topic, news_data)
        
        if not result or "contents" not in result:
             print("[ERROR] Generation failed.")
             print(result)
             return

        new_title = result.get("title")
        new_contents = result.get("contents")
        new_keyword = result.get("search_keyword")
        
        print("\n[Generated Title]:", new_title)
        print("[Generated Contents Start]:", new_contents[:200] + "...")
        
        # 4. Update DB
        print("[INFO] Updating Database...")
        report.title = new_title
        report.contents = new_contents
        report.search_keyword = new_keyword
        
        db.commit()
        print("[SUCCESS] Report 91 updated successfully.")
        
    except Exception as e:
        print(f"[ERROR]: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    # Since generate_balanced_article is synchronous (uses OpenAI sync client), we don't need asyncio
    regenerate_article_91()
