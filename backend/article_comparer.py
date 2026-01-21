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

load_dotenv()

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
# Mock Data (예시)
# ======================================================
now = datetime.now(timezone.utc)
mock_articles = [
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
    {
        "id": 5,
        "company_name": "C경제",
        "title": "화재로 인한 주변 상권 피해액 500억",
        "contents": "이번 화재로 인근 시장의 매출이 80% 급감했다. 경제적 파장이 우려된다.",
        "time": now,
    },
]


# ======================================================
# 유틸: 안전한 JSON 처리/스키마 보정
# ======================================================
TONE_LABELS = ["비판적", "옹호적", "중립적", "건조함", "감정적", "선동적", "냉소적"]


def ensure_company_schema(company_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(data, dict):
        data = {"error": "non-dict"}

    # summary 정규화: 항상 길이 3 리스트
    summary = data.get("summary")
    if isinstance(summary, str):
        lines = [x.strip(" -•\t") for x in summary.splitlines() if x.strip()]
        summary = (lines + [None, None, None])[:3]
    elif isinstance(summary, list):
        summary = (summary + [None, None, None])[:3]
    else:
        summary = [None, None, None]

    # framing 보정
    framing = data.get("framing") if isinstance(data.get("framing"), dict) else {}
    framing_out = {
        "primary_frame": framing.get("primary_frame") or "불명확",
        "blame_target": framing.get("blame_target") or "불명확",
        "policy_orientation": framing.get("policy_orientation") or "불명확",
    }

    # style 보정
    style = data.get("style") if isinstance(data.get("style"), dict) else {}
    intensity = style.get("rhetorical_intensity", 0)
    try:
        intensity = int(intensity)
    except Exception:
        intensity = 0
    intensity = max(0, min(3, intensity))

    style_out = {
        "evidence_style": style.get("evidence_style") or "불명확",
        "rhetorical_intensity": intensity,
    }

    # evidence_quotes 보정: 리스트 + 길이 제한
    quotes = data.get("evidence_quotes")
    if not isinstance(quotes, list):
        quotes = []
    trimmed = []
    for q in quotes[:4]:
        if isinstance(q, str) and q.strip():
            qq = q.strip()
            if len(qq) > 240:
                qq = qq[:240].rstrip() + "…"
            trimmed.append(qq)

    return {
        "company": data.get("company") or company_name,
        "summary": summary,
        "main_cause": data.get("main_cause"),
        "solution": data.get("solution"),
        "framing": framing_out,
        "style": style_out,
        "evidence_quotes": trimmed,
        "selected_article_ids": data.get("selected_article_ids", []),
        "error": data.get("error"),
    }


def normalize_ui_report(report: Dict[str, Any], company_analyses: Dict[str, Any]) -> Dict[str, Any]:
    companies = [c for c in company_analyses.keys()]

    if not isinstance(report, dict):
        report = {}

    report.setdefault("event", {"topic": None, "time_window": None})
    report.setdefault("media_comparison_bullets", [])
    report.setdefault("outlet_cards", [])
    report.setdefault("difference_axes", [])
    report.setdefault("highlights", [])

    # outlet_cards가 비었거나 누락이면 Map 결과로 재구성
    cards = report.get("outlet_cards")
    if not isinstance(cards, list) or len(cards) == 0:
        report["outlet_cards"] = [company_analyses[c] for c in companies]
    else:
        # 카드가 회사 전체를 포함하도록 보정
        existing = {c.get("company") for c in cards if isinstance(c, dict)}
        for c in companies:
            if c not in existing:
                report["outlet_cards"].append(company_analyses[c])

    # difference_axes 보정: 최소 축 구성 + 모든 회사 row 포함 강제
    allowed_axes = {"primary_frame", "blame_target", "policy_orientation", "evidence_style", "rhetorical_intensity"}

    axes = report.get("difference_axes")
    if not isinstance(axes, list):
        axes = []

    # 축이 너무 적으면 기본 5축을 코드로 생성
    if len(axes) < 3:
        axes = []
        # 기본 축 생성
        defaults = [
            ("primary_frame", "핵심 프레임"),
            ("blame_target", "책임 대상"),
            ("policy_orientation", "해결책 성격"),
            ("evidence_style", "근거 스타일"),
            ("rhetorical_intensity", "수사 강도"),
        ]
        for axis, label in defaults:
            rows = []
            for c in companies:
                a = company_analyses[c]
                if axis in {"primary_frame", "blame_target", "policy_orientation"}:
                    val = a["framing"].get(axis, "불명확")
                elif axis == "evidence_style":
                    val = a["style"].get("evidence_style", "불명확")
                else:
                    val = a["style"].get("rhetorical_intensity", 0)
                rows.append({"company": c, "value": val})
            axes.append({"axis": axis, "label": label, "rows": rows})
        report["difference_axes"] = axes
    else:
        # LLM axes를 정리/보정
        normalized_axes = []
        for ax in axes:
            if not isinstance(ax, dict):
                continue
            axis = ax.get("axis")
            if axis not in allowed_axes:
                continue
            label = ax.get("label") or axis

            rows = ax.get("rows")
            if not isinstance(rows, list):
                rows = []

            row_map = {}
            for r in rows:
                if isinstance(r, dict) and r.get("company"):
                    row_map[r["company"]] = r.get("value", "불명확")

            # 회사 전체 포함 강제
            fixed_rows = [{"company": c, "value": row_map.get(c, "불명확")} for c in companies]
            normalized_axes.append({"axis": axis, "label": label, "rows": fixed_rows})

        # 그래도 너무 적으면 기본 축으로 채우기
        if len(normalized_axes) < 3:
            report["difference_axes"] = []
            return normalize_ui_report(report, company_analyses)

        report["difference_axes"] = normalized_axes

    # highlights 최소 보정
    hl = report.get("highlights")
    if not isinstance(hl, list) or len(hl) == 0:
        report["highlights"] = [{"type": "core_conflict", "text": "언론사별 프레임/책임/해결책 관점이 상이함"}]

    return report


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
            combined += f"\n--- [기사 {idx+1} | id={art.get('id')} | 제목: {title}] ---\n" f"{contents}"

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
너는 미디어 분석 AI다. 제공된 기사 묶음을 바탕으로
이 언론사의 관점을 '차이 분석에 적합한 구조'로 추출하라.

[중요 규칙]
- **모든 텍스트 값은 반드시 한국어로 작성하라.**
- 모든 키를 반드시 포함하라. 모르면 null 또는 "불명확"으로 써라.
- summary는 반드시 길이 3의 배열.
- framing과 style은 '주장 방식의 차이'를 드러내는 핵심이다.
- rhetorical_intensity는 기사 표현 강도를 0~3 정수로 평가하라.
- evidence_quotes는 기사 내용에서 직접 발췌한 근거 문장 2~4개.

[출력 JSON 형식]
{
  "company": "언론사명",
  "summary": ["...", "...", "..."],
  "main_cause": "...",
  "solution": "...",
  "framing": {
    "primary_frame": "구조적 실패 | 개인 과실 | 경제 피해 | 복합 | 불명확",
    "blame_target": "정부 | 기관 | 개인 | 기업 | 구조 | 복합 | 불명확",
    "policy_orientation": "처벌 강화 | 제도 개선 | 예산/인프라 | 지원/보상 | 조사/원인규명 | 혼합 | 불명확"
  },
  "style": {
    "evidence_style": "데이터 | 공식발표 | 현장/인터뷰 | 논평/추정 | 혼합 | 불명확",
    "rhetorical_intensity": 0
  },
  "evidence_quotes": ["...", "..."]
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
입력은 언론사별 분석 JSON들의 리스트다(analyses).

너의 목표는 "웹앱 UI에서 바로 렌더링 가능한 최종 JSON"을 출력하는 것이다.

[출력 JSON 형식 - 반드시 준수]
{
  "event": {
    "topic": "사건/이슈 짧은 제목 (불명확하면 null)",
    "time_window": "분석 대상 기간(불명확하면 null)"
  },
  "media_comparison_bullets": [
    "- A일보는 ~~~ (다른 언론사와 차별되는 뚜렷한 특징 한 줄 서술)",
    "- B일보는 ~~~ (다른 언론사와 차별되는 뚜렷한 특징 한 줄 서술)"
  ],
  "outlet_cards": [
    {
      "company": "언론사명",
      "summary": ["...", "...", "..."],
      "framing": {
        "primary_frame": "...",
        "blame_target": "...",
        "policy_orientation": "..."
      },
      "style": {
        "evidence_style": "...",
        "rhetorical_intensity": 0
      },
      "evidence_quotes": ["...", "..."],
      "selected_article_ids": [1, 2, 3]
    }
  ],
  "difference_axes": [
    {
      "axis": "primary_frame | blame_target | policy_orientation | evidence_style | rhetorical_intensity",
      "label": "UI에 표시할 축 이름",
      "rows": [
        { "company": "언론사명", "value": "값(정수 가능)" }
      ]
    }
  ],
  "highlights": [
    { "type": "core_conflict", "text": "가장 큰 대립 쟁점 1문장" },
    { "type": "polarization", "axis": "축 이름", "most_divergent": ["언론사A","언론사B"], "why": "왜 가장 갈리는지" }
  ]
}

[규칙]
- **모든 텍스트 값은 반드시 한국어로 작성하라.**
- **media_comparison_bullets 형식 준수**: 
  반드시 "- [언론사명]은 [특징 서술]" 형태로 작성하라. 
  예: "- 조선일보는 정부의 책임을 강조하며 강력한 처벌을 요구함"
- media_comparison_bullets에는 분석된 **모든 언론사**에 대해 각각 한 줄씩 서술하라.
- outlet_cards에는 입력에 존재하는 모든 언론사를 포함하라.
- difference_axes는 최소 3개 이상 만들고, 가능하면 5개까지.
- rows는 outlet_cards의 언론사들을 모두 포함하라(값이 불명확하면 '불명확').
- 과장 금지. 정보가 없으면 '불명확' 또는 null.
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
            "outlet_cards": [],
            "difference_axes": [],
            "highlights": [{"type": "core_conflict", "text": "결과 생성 실패"}],
            "error": "Reduce returned non-dict",
        }

    data.setdefault("event", {"topic": None, "time_window": None})
    data.setdefault("outlet_cards", [])
    data.setdefault("difference_axes", [])
    data.setdefault("highlights", [])

    data = normalize_ui_report(data, company_analyses)

    return data


# ======================================================
# Main
# ======================================================
async def main():
    print("[Step 1] 기사 데이터 전처리 중...")
    synthesized = get_synthesized_content_by_company(mock_articles, top_n=TOP_N_PER_COMPANY)
    print(f"   -> {len(synthesized)}개 언론사 데이터 병합 완료.")
    for comp, payload in synthesized.items():
        print(f"      - {comp}: selected_article_ids={payload['selected_article_ids']}")

    print("\n[Step 2] 언론사별 개별 분석 진행 (Async)...")
    company_analyses = await process_all_companies_async(synthesized)
    # 예시 출력(안전)
    any_company = next(iter(company_analyses.keys()), None)
    if any_company:
        print(f"   -> 샘플: {any_company} 원인={company_analyses[any_company].get('main_cause')}")

    print("\n[Step 3] 최종 비교 리포트 생성 중...")
    final_report = await generate_final_comparison_report(company_analyses)

    print("\n" + "=" * 60)
    print("📊 최종 비교 분석 결과 (JSON)")
    print("=" * 60)
    print(json.dumps(final_report, indent=2, ensure_ascii=False))

    print("\n" + "=" * 60)
    print("🧩 언론사별 분석 결과 (디버그/검증용)")
    print("=" * 60)
    print(json.dumps(company_analyses, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
