# ai_processor.py
import os
import json
import asyncio  # 병렬 처리를 위해 필요
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from openai import OpenAI, AsyncOpenAI
from database.engine import SessionLocal
from database.crud import create_report
from database.models import Report
from dotenv import load_dotenv

# 🔑 API 키 확인 필수
load_dotenv(override=True)

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError(
        "OPENAI_API_KEY가 설정되지 않았습니다. .env 또는 환경변수를 확인하세요."
    )

client = AsyncOpenAI(api_key=api_key)

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# -------------------------------------------------------------------
# [비동기 처리] 실제 뉴스 분석 로직
# -------------------------------------------------------------------
# from ai_report_generator import generate_balanced_article
from ai_agentic_generator import generate_agentic_article as generate_balanced_article

# from ai_report_comparer import (
#     get_synthesized_content_by_company,
#     process_all_companies_async,
#     generate_final_comparison_report,
# )
from ai_graph_comparer import compare_articles_with_graph, analyze_opinion_articles


from keyword_extractor import KeywordExtractor


async def process_single_issue(
    issue: Report, kw_extractor: KeywordExtractor, db: Session
):
    """단일 이슈 처리 (비동기)"""
    try:
        # 2. 관련 기사 가져오기
        cluster = issue.cluster
        if not cluster or not cluster.news:
            print(f"   -> [Skip] 이슈 ID {issue.report_id}: 연결된 기사가 없습니다.")
            return

        all_articles = cluster.news

        # 팩트 뉴스와 오피니언 분리
        news_articles = [a for a in all_articles if not a.is_opinion]
        opinion_articles = [a for a in all_articles if a.is_opinion]

        print(
            f"   -> [Processing] 이슈 ID {issue.report_id}: '{issue.title}' (뉴스 {len(news_articles)}개, 오피니언 {len(opinion_articles)}개)"
        )

        if not news_articles:
            print(f"   -> [Skip] 팩트 뉴스가 없어 건너뜁니다.")
            return

        # 변환: SQLAlchemy Object -> List[Dict] (팩트 뉴스만)
        articles_data = []
        for art in news_articles:
            articles_data.append(
                {
                    "news_id": art.news_id,
                    "company_name": art.company_name,
                    "title": art.title,
                    "contents": art.contents,
                    "time": art.created_at,
                }
            )

        try:
            # -------------------------------------------------
            # 3-1. 종합 기사 작성 (Sync Call) — 팩트 뉴스만 사용
            # -------------------------------------------------
            summary_result = generate_balanced_article(
                model_name=MODEL, cluster_topic=issue.title, articles=articles_data
            )
            issue.title = summary_result.get(
                "title", issue.title
            )  # AI가 정한 제목으로 업데이트
            issue.contents = summary_result.get("contents", "")
            issue.search_keyword = summary_result.get(
                "search_keyword", ""
            )  # 외신 검색어 저장

            if issue.search_keyword:
                issue.global_search_status = "PENDING"
                issue.search_retry_count = 0
                print(f"      🌍 외신 검색어 추출: {issue.search_keyword}")

            # -------------------------------------------------
            # 3-2. 비교 분석 (GraphRAG-Lite) — 팩트 뉴스만 사용
            # -------------------------------------------------
            final_report = await compare_articles_with_graph(articles_data)

            # -------------------------------------------------
            # 3-2b. 오피니언 분석 (클러스터에 배정된 오피니언이 있으면)
            # -------------------------------------------------
            if opinion_articles:
                opinion_data = [
                    {
                        "news_id": a.news_id,
                        "company_name": a.company_name,
                        "title": a.title,
                        "contents": a.contents,
                        "author": a.author,
                    }
                    for a in opinion_articles
                ]
                opinion_bullets = await analyze_opinion_articles(opinion_data, issue.title)
                if opinion_bullets:
                    final_report["opinion_bullets"] = opinion_bullets
                    print(f"      📝 오피니언 분석: {len(opinion_bullets)}개 언론사")

            issue.analysis_result = final_report

            # -------------------------------------------------
            # 3-3. 키워드 추출 (KeywordExtractor - Hybrid Logic)
            # -------------------------------------------------
            try:
                # issue.contents(요약본) 기반으로 추출
                extracted_kws = kw_extractor.process_content(
                    title=issue.title, content=summary_result.get("contents", "")
                )
                issue.keywords = extracted_kws
                print(f"      🏷️ 키워드: {extracted_kws}")
            except Exception as kw_e:
                print(f"      ⚠️ 키워드 추출 실패 (Skip): {kw_e}")
                issue.keywords = []

            # -------------------------------------------------
            # 3-4. 카테고리 설정 (클러스터 내 가장 많은 카테고리)
            # -------------------------------------------------
            from collections import Counter

            category_ids = [art.category_id for art in news_articles if art.category_id]
            if category_ids:
                # 가장 빈도가 높은 카테고리 선택
                most_common_category = Counter(category_ids).most_common(1)[0][0]
                issue.category_id = most_common_category
                print(f"      📂 카테고리 설정: {most_common_category}")
            else:
                print(f"      ⚠️ 카테고리 정보 없음")

            db.commit()
            print(f"      ✅ 분석 완료: {issue.report_id} (제목: {issue.title})")

        except Exception as e:
            print(f"      🚫 LLM 처리 중 오류: {e}")
            import traceback

            traceback.print_exc()

    except Exception as e:
        print(f"   -> [Error] 이슈 {issue.report_id} 처리 실패: {e}")


async def process_news_async_internal():
    db = SessionLocal()
    kw_extractor = KeywordExtractor()  # Initialize once

    try:
        # 1. 처리되지 않은(Report.contents가 비어있는) 이슈 조회
        targets = (
            db.query(Report)
            .filter((Report.contents == None) | (Report.contents == ""))
            .all()
        )

        print(f"🧠 [AI] 분석 대기 중인 이슈: {len(targets)}건")
        if not targets:
            return

        # 병렬 처리: asyncio.gather로 모든 이슈 동시 처리
        print(f"⚡ [AI] {len(targets)}개 이슈 병렬 처리 시작...")
        tasks = [process_single_issue(issue, kw_extractor, db) for issue in targets]
        await asyncio.gather(*tasks)

        print(f"🎉 [AI] 모든 이슈 처리 완료!")

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
