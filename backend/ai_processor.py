# ai_processor.py
import os
import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from openai import OpenAI, AsyncOpenAI
from database.engine import SessionLocal
from database.crud import create_ai_generated_news
from database.models import AiGeneratedNews
from dotenv import load_dotenv

# 🔑 API 키 확인 필수
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY가 설정되지 않았습니다. .env 또는 환경변수를 확인하세요.")

client = AsyncOpenAI(api_key=api_key)

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# -------------------------------------------------------------------
# [비동기 처리] 실제 뉴스 분석 로직
# -------------------------------------------------------------------
from ai_issue_generator import generate_balanced_article
from article_comparer import (
    get_synthesized_content_by_company,
    process_all_companies_async,
    generate_final_comparison_report,
)


from keyword_extractor import KeywordExtractor


async def process_news_async_internal():
    db = SessionLocal()
    kw_extractor = KeywordExtractor()  # Initialize once

    try:
        # 1. 처리되지 않은(ai_generated_news.contents가 비어있는) 이슈 조회
        targets = (
            db.query(AiGeneratedNews)
            .filter((AiGeneratedNews.contents == None) | (AiGeneratedNews.contents == ""))
            .all()
        )

        print(f"🧠 [AI] 분석 대기 중인 이슈: {len(targets)}건")
        if not targets:
            return

        for issue in targets:
            # 2. 관련 기사 가져오기
            cluster = issue.cluster
            if not cluster or not cluster.news:
                print(f"   -> [Skip] 이슈 ID {issue.id}: 연결된 기사가 없습니다.")
                continue

            articles = cluster.news
            print(f"   -> [Processing] 이슈 ID {issue.id}: '{issue.title}' (기사 {len(articles)}개)")

            # 변환: SQLAlchemy Object -> List[Dict]
            articles_data = []
            for art in articles:
                articles_data.append(
                    {
                        "id": art.id,
                        "company_name": art.company_name,
                        "title": art.title,
                        "contents": art.contents,
                        "time": art.created_at,  # assuming datetime
                    }
                )

            try:
                # -------------------------------------------------
                # 3-1. 종합 기사 작성 (Sync Call)
                # -------------------------------------------------
                summary_result = generate_balanced_article(
                    model_name=MODEL, cluster_topic=issue.title, articles=articles_data
                )
                issue.contents = summary_result  # Markdown text

                # -------------------------------------------------
                # 3-2. 비교 분석 (Async Pipeline)
                # -------------------------------------------------
                # (1) 전처리
                synthesized = get_synthesized_content_by_company(articles_data, top_n=3)
                # (2) 개별 분석
                company_analyses = await process_all_companies_async(synthesized)
                # (3) 최종 리포트
                final_report = await generate_final_comparison_report(company_analyses)

                issue.analysis_result = final_report

                # -------------------------------------------------
                # 3-3. 키워드 추출 (KeywordExtractor - Hybrid Logic)
                # -------------------------------------------------
                try:
                    # issue.contents(요약본) 기반으로 추출
                    extracted_kws = kw_extractor.extract_keywords(text=summary_result, title=issue.title, top_k=10)
                    issue.keywords = extracted_kws
                    print(f"      🏷️ 키워드: {extracted_kws}")
                except Exception as kw_e:
                    print(f"      ⚠️ 키워드 추출 실패 (Skip): {kw_e}")
                    issue.keywords = []

                db.commit()
                print(f"      ✅ 분석 완료: {issue.id} (제목: {issue.title})")

            except Exception as e:
                print(f"      🚫 LLM 처리 중 오류: {e}")
                import traceback

                traceback.print_exc()
                continue

    except Exception as e:
        print(f"🚫 [AI Error] 파이프라인 처리 실패: {e}")
    finally:
        db.close()


def process_news_pipeline():
    """
    백그라운드 스레드에서 호출되는 동기 함수.
    내부적으로 비동기 루프를 실행하여 처리.
    """
    import asyncio

    print("🧠 [AI] 뉴스 분석 파이프라인 가동... (Async / Specialized Modules)")
    asyncio.run(process_news_async_internal())
    print("🧠 [AI] 완료")
