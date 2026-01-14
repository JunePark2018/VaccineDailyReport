import os
import json
import asyncio
from typing import List, Dict, Any
from collections import defaultdict
from datetime import datetime, timedelta
from openai import AsyncOpenAI
from dotenv import load_dotenv

# ======================================================
# 0. 설정 및 Mock Data 준비
# ======================================================

load_dotenv()

# [주의] 실제 실행 시 본인의 API 키를 입력하세요.
api_key = os.getenv("OPENAI_API_KEY")
client = AsyncOpenAI(api_key=api_key)

# 테스트용 Mock Data 생성 (DB에서 가져온 상황 가정)
now = datetime.now()
mock_articles = [
    # [A일보] - 정부 비판조, 시스템 문제 강조
    {
        "id": 1,
        "company_name": "A일보",
        "title": "[종합] 화재 참사, 예견된 인재였다",
        "contents": "이번 화재는 정부의 안전 관리 예산 삭감이 직접적인 원인으로 지목된다. 소방 장비 노후화 문제가 심각하다.",
        "time": now,
    },
    {
        "id": 2,
        "company_name": "A일보",
        "title": "소방관들의 눈물",
        "contents": "현장에 진입한 소방관들은 장비 부족을 호소했다.",
        "time": now,
    },
    # [B뉴스] - 개인 과실 강조, 처벌 강화 주장
    {
        "id": 3,
        "company_name": "B뉴스",
        "title": "화재 원인은 관리자 부주의",
        "contents": "경찰 조사 결과, 건물 관리자가 스프링클러를 꺼둔 것으로 밝혀졌다. 개인의 일탈이 참사를 불렀다.",
        "time": now,
    },
    {
        "id": 4,
        "company_name": "B뉴스",
        "title": "[사설] 안전불감증, 법정 최고형으로 다스려야",
        "contents": "강력한 처벌만이 재발을 막을 수 있다.",
        "time": now,
    },
    # [C경제] - 경제적 손실 강조 (중립/데이터 위주)
    {
        "id": 5,
        "company_name": "C경제",
        "title": "화재로 인한 주변 상권 피해액 500억",
        "contents": "이번 화재로 인근 시장의 매출이 80% 급감했다. 경제적 파장이 우려된다.",
        "time": now,
    },
]


# ======================================================
# Step 1. 기사 선별 및 통합 (Preprocessing)
# ======================================================
def get_synthesized_content_by_company(articles: List[Dict]) -> Dict[str, str]:
    """
    언론사별로 Top 3 기사를 선정해 텍스트를 하나로 합칩니다.
    """
    company_groups = defaultdict(list)
    for article in articles:
        if article.get("company_name"):
            company_groups[article["company_name"]].append(article)

    synthesized_map = {}
    analytic_keywords = ["종합", "분석", "사설", "논평", "심층"]

    for company, group in company_groups.items():
        # 정렬: 키워드 > 길이 > 최신순
        sorted_group = sorted(
            group,
            key=lambda x: (
                any(keyword in x.get("title", "") for keyword in analytic_keywords),
                len(x.get("contents", "") or ""),
                x.get("time"),
            ),
            reverse=True,
        )

        # 상위 3개 합치기
        combined_text = ""
        for idx, art in enumerate(sorted_group[:3]):
            combined_text += f"\n--- [기사 {idx+1}: {art['title']}] ---\n{art.get('contents', '')}"

        synthesized_map[company] = combined_text

    return synthesized_map


# ======================================================
# Step 2. 개별 분석 (Map Phase) - Async
# ======================================================
async def analyze_company_perspective(company_name: str, combined_text: str) -> Dict[str, Any]:
    system_prompt = """
    너는 미디어 분석 AI다. 제공된 기사들을 바탕으로 이 언론사의 '핵심 관점'을 JSON으로 추출해라.
    {
        "company": "언론사명",
        "summary": "핵심 내용 3줄 요약",
        "main_cause": "이 언론사가 지목한 문제의 원인",
        "solution": "이 언론사가 제시한 해결책",
        "tone": "어조 (예: 비판적, 건조함)"
    }
    """
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"언론사: {company_name}\n\n{combined_text}"},
            ],
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"company": company_name, "error": str(e)}


async def process_all_companies_async(synthesized_map: Dict[str, str]) -> Dict[str, Any]:
    tasks = [analyze_company_perspective(comp, text) for comp, text in synthesized_map.items()]
    results = await asyncio.gather(*tasks)
    return {res["company"]: res for res in results if "company" in res}


# ======================================================
# Step 3. 최종 비교 분석 (Reduce Phase)
# ======================================================
async def generate_final_comparison_report(company_analyses: Dict[str, Any]) -> Dict[str, Any]:
    # LLM에 넣어줄 요약본 텍스트 생성
    input_text = ""
    for company, data in company_analyses.items():
        input_text += f"""
        [{company}]
        - 원인 진단: {data.get('main_cause')}
        - 해결책: {data.get('solution')}
        - 어조: {data.get('tone')}
        -------------------
        """

    system_prompt = """
    너는 뉴스 비교 분석가다. 각 언론사의 입장을 비교하여 차이점을 명확히 밝혀라.
    
    [JSON 출력 형식]
    {
        "core_conflict": "언론사 간 가장 크게 대립하는 쟁점 (1문장)",
        "comparison_points": [
            {
                "topic": "비교 항목 (예: 화재 원인)",
                "A_stance": "A일보의 주장",
                "B_stance": "B뉴스의 주장",
                "C_stance": "C경제의 주장"
            }
        ],
        "insight": "종합적인 인사이트 (가급적 A vs B 구도를 부각)"
    }
    """

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": input_text}],
        response_format={"type": "json_object"},
        temperature=0.1,
    )
    return json.loads(response.choices[0].message.content)


# ======================================================
# [Main] 파이프라인 실행
# ======================================================
async def main():
    print("🚀 [Step 1] 기사 데이터 전처리 중...")
    synthesized_data = get_synthesized_content_by_company(mock_articles)
    print(f"   -> {len(synthesized_data)}개 언론사 데이터 병합 완료.")

    print("\n🚀 [Step 2] 언론사별 개별 분석 진행 (Async)...")
    company_analyses = await process_all_companies_async(synthesized_data)
    print(f"   -> 분석 완료. (A일보 원인: {company_analyses['A일보'].get('main_cause')})")

    print("\n🚀 [Step 3] 최종 비교 리포트 생성 중...")
    final_report = await generate_final_comparison_report(company_analyses)

    print("\n" + "=" * 50)
    print("📊 최종 비교 분석 결과 (JSON)")
    print("=" * 50)
    print(json.dumps(final_report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    # Jupyter Notebook 등에서는 await main() 사용
    asyncio.run(main())
