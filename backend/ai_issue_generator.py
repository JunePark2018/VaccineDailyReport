import os
import re
import json
from openai import OpenAI
from dotenv import load_dotenv


load_dotenv(override=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


def generate_balanced_article(model_name: str, cluster_topic: str, articles: list[dict]) -> str:
    """
    cluster_topic: 해당 군집의 주제 (예: 'IT/과학', '경제')
    articles: 해당 군집에 속한 기사 리스트
    """

    model_name = (model_name or "").strip()

    # 0) 사전 체크
    if "gpt" not in model_name.lower():
        return f"⚠️ 지원되지 않는 모델입니다: {model_name} (현재 GPT만 지원)"
    if not openai_client:
        return "⚠️ OpenAI 키 없음"
    if not articles:
        return "⚠️ 기사 소스가 비어 있습니다."

    # 1) 기사 내용 합치기
    context_parts = []
    for idx, art in enumerate(articles, start=1):
        company = art.get("company_name", "언론사 미상")
        title = art.get("title", "제목 없음")
        contents = art.get("contents", "")
        context_parts.append(f"[{idx}] 언론사: {company} | 제목: {title}\n    내용: {contents}\n")
    context_text = "\n".join(context_parts)

    # ------------------------------------------------------------------
    # [Agent 1] Writer Agent (초안 작성)
    # ------------------------------------------------------------------
    def generate_draft():
        system_role = (
            "당신은 '팩트 중심'의 스트레이트 뉴스를 작성하는 **수석 기자**입니다. "
            "주어진 기사 소스들의 팩트만을 조합하여, 가장 객관적이고 건조한 문체로 기사를 작성하십시오."
        )
        user_prompt = f"""
주제: {cluster_topic}
소스로 사용할 기사들:
{context_text}

[지침]
1. 모든 기사의 내용을 종합하되, 중복을 피하십시오.
2. 특정 언론사의 주관적 해석이나 감정적 표현은 제외하고 팩트 위주로 서술하십시오.
3. 기사 구조: [헤드라인] -> [리드] -> [본문] -> [마무리]

응답은 반드시 아래 JSON 형식으로만 출력하십시오:
{{
    "title": "헤드라인",
    "contents": "기사 본문"
}}
"""
        return openai_client.chat.completions.create(
            model=model_name,
            messages=[{"role": "system", "content": system_role}, {"role": "user", "content": user_prompt}],
            response_format={"type": "json_object"},
            temperature=0.3,
        )

    # ------------------------------------------------------------------
    # [Agent 2] Critic Agent (비평 및 검증)
    # ------------------------------------------------------------------
    def generate_critique(draft_title, draft_contents):
        system_role = (
            "당신은 까다롭고 날카로운 **뉴스 데스크 에디터(비평가)**입니다. "
            "작성된 초안을 검토하여 팩트 오류, 편향성, 중복, 문장 호응 등을 지적하십시오."
        )
        user_prompt = f"""
[검토할 초안]
제목: {draft_title}
내용: {draft_contents}

[원본 소스 데이터]
{context_text}

[평가 기준]
1. **팩트 검증**: 원본 소스에 없는 내용이 포함되었는가?
2. **중립성**: 특정 입장에 치우치진 않았는가?
3. **가독성**: 문장이 매끄럽고 중복이 없는가?
4. **구조**: 기사로서 갖춰야 할 형식(리드, 본문 등)이 적절한가?

위 기준에 따라 **구체적인 수정 지시사항**을 3~5가지 항목으로 정리해 주세요.
잘못된 점이 없다면 "수정 사항 없음"이라고 하십시오.
"""
        return openai_client.chat.completions.create(
            model=model_name,
            messages=[{"role": "system", "content": system_role}, {"role": "user", "content": user_prompt}],
            temperature=0.1,
        )

    # ------------------------------------------------------------------
    # [Agent 3] Refiner Agent (최종 수정)
    # ------------------------------------------------------------------
    def generate_final(draft_title, draft_contents, critique):
        system_role = (
            "당신은 **최종 편집장**입니다. "
            "비평가(Critic)의 지적을 수용하여 기사를 완성도 높게 수정하십시오."
            "또한 글로벌 독자를 위해 이 이슈의 핵심 영문 검색어(keyword)를 하나 추출하십시오."
        )
        user_prompt = f"""
[초안]
제목: {draft_title}
내용: {draft_contents}

[비평가의 지적]
{critique}

위 지적 사항을 반영하여 기사를 **최종 수정**하십시오.
특히 "영상에서 보듯", "사진과 같이" 같은 멀티미디어 참조 문구는 모두 삭제하십시오.

[출력 형식 - JSON]
{{
    "title": "최종 수정된 제목",
    "contents": "최종 수정된 본문",
    "search_keyword": "영문 검색어 (예: Samsung earnings shock)"
}}
"""
        return openai_client.chat.completions.create(
            model=model_name,
            messages=[{"role": "system", "content": system_role}, {"role": "user", "content": user_prompt}],
            response_format={"type": "json_object"},
            temperature=0.2,
        )

    # ------------------------------------------------------------------
    # [Orchestration] 실행 파이프라인
    # ------------------------------------------------------------------
    try:
        # 1. Draft
        print("🤖 [Writer] 초안 작성 중...")
        draft_resp = generate_draft()
        draft_data = json.loads(draft_resp.choices[0].message.content)

        # 2. Critique
        print("🧐 [Critic] 기사 비평 및 검증 중...")
        critic_resp = generate_critique(draft_data.get("title"), draft_data.get("contents"))
        feedback = critic_resp.choices[0].message.content
        print(f"📝 [Critic Feedback]: {feedback}")

        # 3. Refine
        print("✍️ [Refiner] 최종 기사 편집 중...")
        final_resp = generate_final(draft_data.get("title"), draft_data.get("contents"), feedback)
        final_data = json.loads(final_resp.choices[0].message.content)

        return final_data

    except Exception as e:
        print(f"⚠️ 에러 발생: {str(e)}")
        import traceback

        traceback.print_exc()
        return {"title": "생성 실패", "contents": f"AI 처리 중 오류가 발생했습니다: {str(e)}", "search_keyword": ""}
