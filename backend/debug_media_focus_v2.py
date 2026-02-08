
from database.engine import SessionLocal
from database.models import News, Company, Report, Cluster
from sqlalchemy import func

def debug_db():
    db = SessionLocal()
    try:

        # 1. Check Report 82
        reports = db.query(Report).filter(Report.report_id == 82).all()
        print(f"Checking Report 82...")

        for report in reports:
            # Check Media Focus Stats
            # Use correct ID
            target_id = report.cluster_id
            print(f" -> Querying Media Focus for ClusterID={target_id} (ReportID={report.report_id})")
            
            from database.crud import get_media_focus_stats
            stats = get_media_focus_stats(db, target_id)
            mf = stats.get("media_focus", [])
            
            if not mf:
                print(f"\n[PROBLEM] Report [{report.report_id}] {report.title[:20]}... -> Media Focus Empty")
                if not report.cluster:
                     print("Reason: No cluster")
                elif not report.cluster.news:
                     print("Reason: No news in cluster")
                else:
                     print(f"Reason: Cluster has {len(report.cluster.news)} news.")
                     dates = []
                     for n in report.cluster.news:
                         cname = n.company.name if n.company else "None"
                         print(f"      - News {n.news_id}: {n.created_at} | {cname}")
                         dates.append(n.created_at)
                     
                     if dates:
                         from datetime import datetime, timedelta
                         min_date = min(dates)
                         print(f"    Min Date: {min_date}")
                         print(f"    Current Time: {datetime.now()}")
                         if min_date < datetime.now() - timedelta(hours=720):
                             print("    ❌ News is older than 30 days. get_media_focus_stats uses datetime.now()!")
            else:
                 print(f"✅ Report [{report.report_id}] OK (Focus Count: {len(mf)})")
                 for item in mf:
                     print(f"   - {item}")

    finally:
        db.close()

if __name__ == "__main__":
    debug_db()
