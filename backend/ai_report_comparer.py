import os
import json
import asyncio
import random
from typing import List, Dict, Any, Tuple
from collections import defaultdict
from datetime import datetime, timezone
from openai import AsyncOpenAI
from dotenv import load_dotenv

# ======================================================
# 0) 설정
# ======================================================

load_dotenv(override=True)

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY가 설정되지 않았습니다. .env 또는 환경변수를 확인하세요.")

client = AsyncOpenAI(api_key=api_key)

MODEL = os.getenv("5.2", "gpt-4o-mini")

# 운영 기본값 (상황에 맞게 조정)
TOP_N_PER_COMPANY = 3
MAX_CONCURRENCY = 8
MAX_RETRIES = 5
BASE_BACKOFF_SECONDS = 0.6

# 카테고리별 시스템 프롬프트 정의
CATEGORY_PROMPTS = {
    "정치": """
[분석 관점: 정치/이데올로기]
이 기사들은 **정치적 역학 관계, 정당의 입장, 이데올로기 차이**를 다루고 있습니다.
- **핵심 인물/정당**의 발언과 행보에 드러난 정치적 의도를 파악하십시오.
- 특정 정책이나 사안에 대해 **지지(옹호)하는지 비판(공격)하는지** 명확히 구분하십시오.
- 보수/진보 등 언론사의 전통적 성향이 반영되었는지 분석하십시오.
""",
    "경제": """
[분석 관점: 경제/시장]
이 기사들은 **시장 동향, 기업 전략, 소비자 영향, 거시 경제 지표**를 다루고 있습니다.
- **수치(주가, 금리, 실적 등)**와 그 해석에 주목하십시오.
- 특정 경제 정책이나 기업 활동이 **시장에 긍정적인지 부정적인지** 평가하십시오.
- 투자자, 소비자, 기업 등 **이해관계자별 유불리**를 어떻게 묘사하는지 분석하십시오.
""",
    "사회": """
[분석 관점: 사회/공공]
이 기사들은 **사회 문제, 사건/사고, 여론, 공공 안전, 인권**을 다루고 있습니다.
- 사건의 **원인과 책임 소재**를 어디에 두고 있는지 분석하십시오.
- **피해자 vs 가해자**, **시스템적 문제 vs 개인적 일탈** 등 프레임을 파악하십시오.
- 갈등 사안에 대해 **해법을 제시하는지, 갈등을 부각하는지** 확인하십시오.
""",
    "국제": """
[분석 관점: 국제/외교]
이 기사들은 **국가 간 관계, 지정학적 리스크, 국익**을 다루고 있습니다.
- **자국의 이익(국익)** 관점에서 타국을 어떻게 묘사하는지 분석하십시오.
- 외교적 수사(Rhetoric) 뒤에 숨겨진 **실리적 계산**을 파악하십시오.
""",
    "IT/과학": """
[분석 관점: 기술/혁신]
이 기사들은 **기술 혁신, 산업 트렌드, 윤리적 문제**를 다루고 있습니다.
- 신기술에 대해 **낙관적(기대)**인지 **비관적(우려)**인지 분석하십시오.
- 기술의 **실용성과 파급 효과**에 초점을 맞추는지, **부작용과 규제**에 초점을 맞추는지 확인하십시오.
""",
    "default": """
[분석 관점: 일반/객관]
- 사실 관계를 중심으로 차분하게 분석하십시오.
- 감정적 어조를 배제하고 객관적인 톤을 유지하십시오.
""",
}

# ======================================================
# 유틸: 안전한 JSON 처리/스키마 보정
# ======================================================


def ensure_company_schema(company_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(data, dict):
        data = {"error": "non-dict"}

    return {
        "company": data.get("company") or company_name,
        "title": data.get("title") or "제목 없음",
        "body": data.get("body") or "내용 없음",
        "error": data.get("error"),
        "selected_article_ids": data.get("selected_article_ids", []),
    }


def ensure_reduce_schema(data: dict) -> dict:
    if not isinstance(data, dict):
        return {"media_comparison_bullets": [], "error": "non-dict"}

    bullets = data.get("media_comparison_bullets", [])
    if not isinstance(bullets, list):
        bullets = []

    # Filter out invalid items, keep dicts (new) and strs (old/fallback)
    valid_bullets = [b for b in bullets if isinstance(b, (str, dict))]

    return {"media_comparison_bullets": valid_bullets, "error": data.get("error")}


def safe_json_loads(s: str) -> Dict[str, Any]:
    try:
        return json.loads(s)
    except Exception:
        # 최후의 수단: 빈 dict
        return {}


# ======================================================
# Step 1) 기사 선별 및 통합 (기사만, 다양성 규칙 제외)
# ======================================================
def pick_top_articles(group: List[Dict[str, Any]], top_n: int) -> List[Dict[str, Any]]:
    analytic_keywords = ["종합", "분석", "사설", "논평", "심층"]

    def score(article: Dict[str, Any]) -> Tuple[int, int, datetime]:
        title = article.get("title", "") or ""
        contents = article.get("contents", "") or ""
        # 키워드 포함 여부(bool) 대신 "키워드 포함 개수"로 개선
        kw_score = sum(1 for k in analytic_keywords if k in title)
        length_score = len(contents)
        t = article.get("time") or datetime.min.replace(tzinfo=timezone.utc)
        return (kw_score, length_score, t)

    return sorted(group, key=score, reverse=True)[:top_n]


def get_synthesized_content_by_company(
    articles: List[Dict[str, Any]],
    top_n: int = TOP_N_PER_COMPANY,
) -> Dict[str, Dict[str, Any]]:
    """
    return:
      {
        "A일보": {
           "combined_text": "...",
           "selected_article_ids": [1,2, ...]
        },
        ...
      }
    """
    company_groups = defaultdict(list)
    for a in articles:
        c = a.get("company_name")
        if c:
            company_groups[c].append(a)

    synthesized = {}
    for company, group in company_groups.items():
        picked = pick_top_articles(group, top_n=top_n)

        combined = ""
        selected_ids = []
        for idx, art in enumerate(picked):
            selected_ids.append(art.get("id"))
            title = art.get("title", "")
            contents = art.get("contents", "")
            combined += (
                f"\n--- [기사 {idx+1} | id={art.get('id')} | url={art.get('url')} | 제목: {title}] ---\n{contents}"
            )

        synthesized[company] = {
            "combined_text": combined.strip(),
            "selected_article_ids": selected_ids,
        }

    return synthesized


# ======================================================
# 공통: OpenAI 호출 (재시도 + 백오프)
# ======================================================
async def call_llm_json(messages: List[Dict[str, str]], temperature: float = 0.2) -> Dict[str, Any]:
    last_err = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = await client.chat.completions.create(
                model=MODEL,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=temperature,
            )
            content = resp.choices[0].message.content or "{}"
            return safe_json_loads(content)

        except Exception as e:
            last_err = e
            # 간단한 지수 백오프 + 지터
            sleep_s = BASE_BACKOFF_SECONDS * (2 ** (attempt - 1)) + random.random() * 0.25
            await asyncio.sleep(sleep_s)

    return {"error": f"LLM call failed after retries: {last_err}"}


# ======================================================
# Step 2) 개별 분석 (Map Phase) - Async + Semaphore
# ======================================================
def build_company_system_prompt(category_name: str = None) -> str:
    base_prompt = """
너는 전문 뉴스 편집자(Editor)이자 **데이터 분석가**이다.
제공된 여러 개의 기사들은 모두 **동일한 언론사**에서 특정 이슈에 대해 보도한 것들이다.
너의 임무는 이 기사들의 내용을 종합하여,
1. **종합 기사(Comprehensive Article)**를 작성하고,
2. **지식 그래프(Graph Construction)**를 위한 [핵심 개체(Entity) - 입장(Stance)] 데이터를 추출하는 것이다.
"""
    # 카테고리별 추가 지침 삽입
    category_instruction = CATEGORY_PROMPTS.get(category_name, CATEGORY_PROMPTS["default"])

    return f"""{base_prompt}

{category_instruction}

[작성 규칙]
1. **관점 유지**: 해당 언론사의 고유한 색채(Tone & Manner)를 유지하라.
2. **사실 통합**: 여러 기사의 팩트를 시간순/논리순으로 통합하라.
3. **GraphRAG 추출**: 기사에서 다루는 핵심 인물, 조직, 정책(Entity)에 대해 이 언론사가 긍정적인지 비판적인지 분석하라.
   - **중요**: 만약 기사가 명확한 호불호 없이 **단순 사실(Fact) 위주**로 보도했다면, 억지로 긍정/부정으로 분류하지 말고 **"사실 전달(Factual)"** 또는 **"객관적(Objective)"**으로 분류하라.

[출력 JSON 형식]
{{
  "company": "언론사명",
  "title": "대표 제목 (언론사 논조 반영)",
  "body": "종합된 기사 본문 (3문단 내외)",
  "graph_entities": [
    {{
      "name": "대상(인물/조직/정책)",
      "stance": "긍정/부정/중립/비판/옹호/사실 전달/객관적",
      "description": "이 대상을 어떻게 묘사하는지 한 줄 요약"
    }}
  ]
}}
""".strip()


async def analyze_company_perspective(
    sem: asyncio.Semaphore,
    company_name: str,
    combined_text: str,
    selected_article_ids: List[Any],
    category_name: str = None,
) -> Dict[str, Any]:
    async with sem:
        system_prompt = build_company_system_prompt(category_name)
        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": (f"언론사: {company_name}\n" f"선정 기사 id: {selected_article_ids}\n\n" f"{combined_text}"),
            },
        ]

        data = await call_llm_json(messages, temperature=0.2)

        # 보정 로직
        if isinstance(data, dict):
            data["selected_article_ids"] = selected_article_ids
            # graph_entities가 없으면 빈 리스트 추가
            if "graph_entities" not in data:
                data["graph_entities"] = []

        return ensure_company_schema(company_name, data)


def ensure_company_schema(company_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(data, dict):
        data = {"error": "non-dict"}

    return {
        "company": data.get("company") or company_name,
        "title": data.get("title") or "제목 없음",
        "body": data.get("body") or "내용 없음",
        "graph_entities": data.get("graph_entities", []),
        "error": data.get("error"),
        "selected_article_ids": data.get("selected_article_ids", []),
    }


async def process_all_companies_async(
    synthesized_map: Dict[str, Dict[str, Any]], category_name: str = None
) -> Dict[str, Any]:
    sem = asyncio.Semaphore(MAX_CONCURRENCY)
    tasks = []
    print(f"   [AI] Category-Specific Analysis: {category_name or 'Default'}")
    for comp, payload in synthesized_map.items():
        tasks.append(
            analyze_company_perspective(
                sem=sem,
                company_name=comp,
                combined_text=payload["combined_text"],
                selected_article_ids=payload["selected_article_ids"],
                category_name=category_name,
            )
        )

    results = await asyncio.gather(*tasks)
    # {company: analysis}
    return {r["company"]: r for r in results if isinstance(r, dict) and r.get("company")}


# ======================================================
# Step 3) 최종 비교 분석 (Reduce Phase) - 확장형 포맷
# ======================================================
def build_reduce_system_prompt_ui() -> str:
    return """
너는 **심층 뉴스 비교 분석가(GraphRAG Analyst)**다.
입력은 각 언론사별 '종합 기사'와 **'개체-입장(Entity-Stance) 그래프 데이터'**이다.

너의 목표는 텍스트와 그래프 데이터를 모두 활용하여, **가장 날카롭고 통찰력 있는 비교 분석**을 수행하는 것이다.
단순히 "A는 이랬고, B는 저랬다"는 나열이 아니라, **"어떤 대상에 대해 시각이 어떻게 엇갈리는지"**를 포착하라.

[출력 JSON 형식]
{
  "media_comparison_bullets": [
    {
      "analysis": "- 언론사A는 [대상]에 대해 ... (기존과 동일)",
      "summary": "핵심 키워드 요약 (단어+특수기호 위주)"
    },
    {
      "analysis": "- 언론사B는 [대상]을 ...",
      "summary": "..."
    }
  ]
}

[작성 규칙]
1. **Graph 활용**: 입력된 `graph_entities` 정보를 적극 활용하여, 특정 인물이나 정책에 대한 입장 차이를 부각하라.
2. **사실 우선**: 만약 'stance'가 "사실 전달"이나 "객관적"이라면, 이를 억지로 긍정/부정으로 해석하지 말고 "차분히 사실 관계를 전했습니다" 또는 "객관적인 태도를 유지했습니다"와 같이 있는 그대로 서술하라.
3. **표현의 다양성**: 입장 차이를 부각할 때, "반면", "한편", "이와 달리", "대조적으로" 등 다양한 접속사를 활용하거나, 문장을 아예 분리하여 서술하라.
4. **언어**: 한국어 작성, 어미는 '~니다' 사용.
5. **포괄성**: 모든 언론사를 한 줄씩 언급. **언론사 이름에는 절대 대괄호([])를 사용하지 마시오.**
6. **Summary 작성**: 'summary' 필드는 모바일 화면에서도 한눈에 들어오도록, 서술어가 아닌 **키워드와 화살표(->), 등호(=) 등 기호**를 사용하여 매우 짧게 요약하라. (예: "A일보: 성장 긍정 -> 투자 확대")
""".strip()


async def generate_final_comparison_report(company_analyses: Dict[str, Any]) -> Dict[str, Any]:
    analyses_list = list(company_analyses.values())

    system_prompt = build_reduce_system_prompt_ui()
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": json.dumps({"analyses": analyses_list}, ensure_ascii=False)},
    ]

    data = await call_llm_json(messages, temperature=0.1)

    # 최소 보정(프론트가 깨지지 않게)
    if not isinstance(data, dict):
        return {
            "event": {"topic": None, "time_window": None},
            "media_comparison_bullets": [],
            "error": "Reduce returned non-dict",
        }

    data.setdefault("media_comparison_bullets", [])

    return ensure_reduce_schema(data)
