import sys
import os
import asyncio
import random
from datetime import datetime

# Add Backend root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.orm import Session
from database.engine import SessionLocal
from database import models, crud
from ai_agentic_generator import generate_agentic_article

# Sample Dummy Data (Raw Articles) to mimic crawling
SAMPLE_TOPIC = "OpenAI, 차세대 AI 모델 'GPT-5' 전격 공개"
SAMPLE_ARTICLES = [
    {
        "company_name": "TechDaily",
        "title": "OpenAI unveils GPT-5 with reasoning capabilities",
        "contents": "OpenAI has officially announced GPT-5. It features enhanced reasoning and 10x faster processing speed compared to GPT-4. Sam Altman called it a 'significant leap forward'.",
        "time": "2024-05-20 10:00:00"
    },
    {
        "company_name": "Korea IT News",
        "title": "오픈AI, GPT-5 발표... AGI 시대 성큼",
        "contents": "오픈AI가 새로운 플래그십 모델 GPT-5를 공개했다. 한국어 처리 능력이 대폭 향상되었으며, 멀티모달 기능이 강화되었다. 업계는 AGI 도달 가능성에 주목하고 있다.",
        "time": "2024-05-20 10:05:00"
    },
    {
        "company_name": "AI Times",
        "title": "GPT-5, 무엇이 달라졌나? 비용은 낮추고 성능은 올리고",
        "contents": "GPT-5의 API 비용은 GPT-4 Turbo의 절반 수준으로 책정되었다. 또한 '비평가 모드'가 탑재되어 스스로 오류를 검증하는 기능이 추가된 것이 특징이다.",
        "time": "2024-05-20 10:10:00"
    },
    {
        "company_name": "The Verge",
        "title": "OpenAI's GPT-5 is here to challenge Gemini",
        "contents": "The competition heats up as OpenAI releases GPT-5. Experts say it outperforms Google's Gemini Ultra in coding benchmarks. Microsoft Azure will support it immediately.",
        "time": "2024-05-20 10:15:00"
    }
]

def insert_sample_data():
    db = SessionLocal()
    try:
        print(f"🚀 Starting Sample Data Injection for: {SAMPLE_TOPIC}")

        # 1. Create Companies if not exist
        company_map = {}
        for art in SAMPLE_ARTICLES:
            c_name = art["company_name"]
            company = crud.get_company_by_name(db, c_name)
            if not company:
                company = models.Company(name=c_name)
                db.add(company)
                db.flush()
            company_map[c_name] = company.company_id

        # 2. Create Cluster
        cluster = crud.create_cluster(db, title=SAMPLE_TOPIC)
        print(f"✅ Created Cluster ID: {cluster.cluster_id}")

        # 3. Insert Raw News & Link to Cluster
        news_ids = []
        for i, art in enumerate(SAMPLE_ARTICLES):
            news = crud.create_news(
                db,
                title=art["title"],
                contents=art["contents"],
                url=f"http://sample-news-{random.randint(1000,9999)}.com/{i}",
                company_id=company_map[art["company_name"]],
                category="IT/과학",
                created_at=datetime.strptime(art["time"], "%Y-%m-%d %H:%M:%S")
            )
            # Link to cluster
            crud.add_news_to_cluster(db, cluster_id=cluster.cluster_id, news_id=news.news_id)
            news_ids.append(news.news_id)
            
        db.commit()
        print(f"✅ Inserted {len(news_ids)} raw articles.")

        # 4. Generate AI Summary using AGENTIC WORKFLOW
        print("🤖 Generating AI Report (Writer-Critic Loop)... Please wait...")
        
        # Prepare articles for generator (needs company_name key)
        # generator expects list of dicts. SAMPLE_ARTICLES already has this structure.
        
        result = generate_agentic_article(
            model_name="gpt-4o-mini",
            cluster_topic=SAMPLE_TOPIC,
            articles=SAMPLE_ARTICLES
        )

        print("✨ AI Generation Complete!")
        print(f"   - Title: {result.get('title')}")
        print(f"   - Status: Agentic process finished.")

        # 5. Insert AiGeneratedNews
        ai_news = crud.create_ai_generated_news(
            db,
            cluster_id=cluster.cluster_id,
            category_id=None, # Optional
            title=result.get("title"),
            contents=result.get("contents"),
            keywords=[],
            analysis_result={"agentic_log": "Generated via Writer-Critic Workflow"}
        )
        
        db.commit()
        print(f"🎉 Successfully inserted AI News ID: {ai_news.ai_generated_news_id}")

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    insert_sample_data()
