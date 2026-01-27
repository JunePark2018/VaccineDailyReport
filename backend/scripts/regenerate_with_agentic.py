import sys
import os

# Add Backend root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.orm import Session
from database.engine import SessionLocal
from database import models, crud
from ai_agentic_generator import generate_agentic_article
from ai_graph_comparer import compare_articles_with_graph # New Import
import asyncio

async def regenerate_existing_cluster():
    """
    실제 크롤링된 기사가 있는 클러스터를 선택해서,
    Agentic Workflow로 다시 생성하고 기존 AI 생성 기사를 업데이트합니다.
    """
    db = SessionLocal()
    try:
        # 1. 기존 클러스터 중에서 기사가 많은 것 하나 선택
        print("🔍 Searching for existing clusters with articles...")
        
        # 클러스터 중 연결된 기사가 2개 이상인 것 찾기
        clusters = db.query(models.Cluster).all()
        valid_clusters = []
        
        for cluster in clusters:
            if len(cluster.news) >= 2:  # 최소 2개 이상의 기사가 있어야 함
                valid_clusters.append({
                    "cluster_id": cluster.cluster_id,
                    "title": cluster.title,
                    "article_count": len(cluster.news)
                })
        
        # [User Request] Force regenerate Cluster ID 44 (Linked to News 36)
        TARGET_CLUSTER_ID = 44
        target = {"cluster_id": TARGET_CLUSTER_ID}
        
        # Check if it exists
        cluster = db.query(models.Cluster).filter(models.Cluster.cluster_id == TARGET_CLUSTER_ID).first()
        if not cluster:
            print(f"❌ Cluster ID {TARGET_CLUSTER_ID} not found!")
            return

        target["title"] = cluster.title
        target["article_count"] = len(cluster.news)
        
        print(f"✅ Selected Target Cluster ID: {target['cluster_id']}")
        print(f"   Title: {target['title']}")
        print(f"   Articles: {target['article_count']}")
        
        # 2. 해당 클러스터의 실제 기사 데이터 가져오기
        cluster = db.query(models.Cluster).filter(
            models.Cluster.cluster_id == target['cluster_id']
        ).first()
        
        articles_data = []
        for news in cluster.news:
            articles_data.append({
                "news_id": news.news_id,
                "company_name": news.company.name if news.company else "Unknown",
                "title": news.title or "No Title",
                "contents": news.contents or "",
                "time": news.created_at.strftime("%Y-%m-%d %H:%M:%S") if news.created_at else ""
            })
        
        print(f"📰 Loaded {len(articles_data)} articles:")
        for i, art in enumerate(articles_data[:3], 1):  # Show first 3
            print(f"   [{i}] {art['company_name']}: {art['title'][:50]}...")
        
        # 3. Agentic Workflow 실행
        print("\n🤖 Running Agentic Workflow (Writer-Critic Loop)...")
        result = generate_agentic_article(
            model_name="gpt-4o-mini",
            cluster_topic=target['title'],
            articles=articles_data
        )
        
        print("\n✨ AI Generation Complete!")
        print(f"   📌 New Title: {result.get('title')[:80]}...")
        print(f"   📊 Content Length: {len(result.get('contents', ''))} chars")

        # 3-1. Run GraphRAG Comparative Analysis
        print("\n🕸️ Running GraphRAG Comparative Analysis...")
        # Need to pass list of dicts (which we already prepared as 'articles_data')
        comparison_result = await compare_articles_with_graph(articles_data)
        print("   ✅ Graph Analysis Complete!")
        print(f"   bullets: {comparison_result.get('media_comparison_bullets')}")
        
        # 4. 기존 AI 생성 기사 업데이트 (또는 새로 생성)
        ai_news = db.query(models.AiGeneratedNews).filter(
            models.AiGeneratedNews.cluster_id == target['cluster_id']
        ).first()
        
        if ai_news:
            # 기존 기사 업데이트
            ai_news.title = result.get("title")
            ai_news.contents = result.get("contents")
            ai_news.search_keyword = result.get("search_keyword", "")
            ai_news.analysis_result = comparison_result # Update Analysis
            print(f"\n🔄 Updated existing AI News ID: {ai_news.ai_generated_news_id}")
        else:
            # 새로 생성
            ai_news = crud.create_ai_generated_news(
                db,
                cluster_id=target['cluster_id'],
                title=result.get("title"),
                contents=result.get("contents"),
                keywords=[],
                analysis_result=comparison_result # Save Analysis
            )
            print(f"\n➕ Created new AI News ID: {ai_news.ai_generated_news_id}")
        
        db.commit()
        print("\n🎉 Success! Check the frontend to see the agentic-generated article.")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(regenerate_existing_cluster())
