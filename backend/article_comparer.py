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

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# 운영 기본값 (상황에 맞게 조정)
TOP_N_PER_COMPANY = 3
MAX_CONCURRENCY = 8
MAX_RETRIES = 5
BASE_BACKOFF_SECONDS = 0.6

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

    # 문자열 아닌 항목 제거
    bullets = [b for b in bullets if isinstance(b, str)]

    return {"media_comparison_bullets": bullets, "error": data.get("error")}


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
def build_company_system_prompt() -> str:
    return """
너는 전문 뉴스 편집자(Editor)이다.
제공된 여러 개의 기사들은 모두 **동일한 언론사**에서 특정 이슈에 대해 보도한 것들이다.

너의 임무는 이 기사들의 내용을 모두 종합하여, **중복을 제거하고 하나의 완벽한 종합 기사(Comprehensive Article)**로 재작성하는 것이다.

[작성 규칙]
1. **관점 유지**: 원본 기사들의 논조, 프레임, 주요 주장, 단어 선택 등 **해당 언론사의 고유한 색채(Tone & Manner)**를 그대로 유지해야 한다.
2. **사실 통합**: 여러 기사에 흩어져 있는 팩트들을 시간순이나 논리적 순서에 맞게 통합하라.
3. **중복 제거**: 똑같은 내용이 반복되지 않도록 하라.
4. **언어**: 반드시 **한국어**로 작성하라.
5. **근거 제한**: 제공된 기사들에 등장하지 않는 사실/수치/인용/고유명사는 절대 추가하지 마라.
6. **불확실성 표기**: 기사들 간 내용이 엇갈리면 단정하지 말고 "기사마다 다르게 전한다"처럼 표기하라.

[출력 JSON 형식]
{
  "company": "언론사명",
  "title": "이 모든 기사를 아우르는 대표 제목 (언론사의 논조 반영)",
  "body": "종합된 기사 본문 (3~5문단 분량, 내용 충실하게)"
}
""".strip()


async def analyze_company_perspective(
    sem: asyncio.Semaphore,
    company_name: str,
    combined_text: str,
    selected_article_ids: List[Any],
) -> Dict[str, Any]:
    async with sem:
        system_prompt = build_company_system_prompt()
        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": (f"언론사: {company_name}\n" f"선정 기사 id: {selected_article_ids}\n\n" f"{combined_text}"),
            },
        ]

        data = await call_llm_json(messages, temperature=0.2)
        # selected ids 넣어두기(추적 가능하게)
        if isinstance(data, dict):
            data["selected_article_ids"] = selected_article_ids
        return ensure_company_schema(company_name, data)


async def process_all_companies_async(synthesized_map: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    sem = asyncio.Semaphore(MAX_CONCURRENCY)
    tasks = []
    for comp, payload in synthesized_map.items():
        tasks.append(
            analyze_company_perspective(
                sem=sem,
                company_name=comp,
                combined_text=payload["combined_text"],
                selected_article_ids=payload["selected_article_ids"],
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
너는 뉴스 비교 분석가다.
입력은 **각 언론사별로 종합된 '대표 기사(Synthesized Article)'들의 리스트**이다.

너의 목표는 이 기사들을 정밀하게 비교 독해하여, **"웹앱 UI에서 바로 렌더링 가능한 최종 JSON"**을 출력하는 것이다.
UI 요소는 모두 배제하고, 오직 **"언론사별 비교 요약(media_comparison_bullets)"의 품질**에만 집중하라.

[출력 JSON 형식 - 반드시 준수]
{
  "media_comparison_bullets": [
    "- A일보는 ...",
    "- B일보는 ..."
  ]
}

[핵심 규칙 - media_comparison_bullets 작성법]
1. **형식 준수**: 반드시 "- [언론사명]은 [특징 서술]" 형태로 작성하라.
2. **언어**: **모든 텍스트는 한국어로 작성하라.**
3. **비교 분석(Deep Comparison)**:
   - 각 언론사가 재구성한 기사의 **헤드라인, 강조하는 팩트, 책임 소재를 묻는 대상, 해결책 제시 방향** 등을 비교하라.
   - 단순 요약이 아니라, **"다른 언론사와 무엇이 다른지"**를 짚어내는 것이 핵심이다.
   - 예: "A일보는 '인재'임을 강조하며 정부 책임을 강하게 묻는 반면, B일보는 '불가항력'적 측면 부각하며 시민 의식 개선을 촉구함"
4. **포괄성**: 입력된 **모든 언론사**에 대해 빠짐없이 한 줄씩 작성하라.
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
