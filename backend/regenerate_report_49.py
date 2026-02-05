import asyncio
import os
import sys

# Add backend directory to sys.path to resolve imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from database.engine import SessionLocal
from database.models import Report
from ai_processor import process_single_issue
from keyword_extractor import KeywordExtractor


async def main():
    print("Starting regeneration for Report ID 49...")
    db = SessionLocal()
    try:
        # Fetch Report 49
        report = db.query(Report).get(49)
        if not report:
            print("❌ Report 49 not found in database!")
            return

        print(f"Target Report: {report.title} (ID: 49)")

        # Initialize Keyword Extractor
        print("Initializing Keyword Extractor...")
        kw_extractor = KeywordExtractor()

        # Run Pipeline
        print("Running AI Pipeline...")
        await process_single_issue(report, kw_extractor, db)

        print("✅ Report regenerated successfully.")

    except Exception as e:
        print(f"❌ Error during regeneration: {e}")
        import traceback

        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
