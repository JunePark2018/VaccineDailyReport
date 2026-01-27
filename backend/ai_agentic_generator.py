import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(override=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

def generate_agentic_article(model_name: str, cluster_topic: str, articles: list[dict]) -> dict:
    """
    Agentic Workflow (Writer -> Critic -> Editor) for generating high-quality news reports.
    
    Roles:
    1. Writer: Writes the initial draft based on source articles.
    2. Critic: Reviews the draft for factuality, neutrality, and missing info.
    3. Editor: Refines the draft if the Critic has feedback.
    """
    
    # 0) Pre-check
    model_name = (model_name or "").strip()
    if "gpt" not in model_name.lower():
        return {"title": "오류", "contents": f"⚠️ 지원되지 않는 모델: {model_name}", "search_keyword": ""}
    if not openai_client:
        return {"title": "오류", "contents": "⚠️ OpenAI API 키 없음", "search_keyword": ""}
    if not articles:
        return {"title": "오류", "contents": "⚠️ 원본 기사 없음", "search_keyword": ""}

    # 1) Prepare Context
    context_parts = []
    for idx, art in enumerate(articles, start=1):
        company = art.get("company_name", "언론사 미상")
        title = art.get("title", "제목 없음")
        contents = art.get("contents", "")
        time = art.get("time", "")
        context_parts.append(f"[{idx}] 언론사: {company} | 제목: {title}\n    시간: {time}\n    내용: {contents}\n")
    context_text = "\n".join(context_parts)

    print(f"   🤖 [Agentic] 주제: {cluster_topic}")

    # ======================================================================================
    # Step 1: Writer Agent (Initial Draft)
    # ======================================================================================
    writer_system = (
        "당신은 한국의 전문 뉴스 기자입니다. 여러 원본 기사를 읽고 객관적이고 균형잡힌 종합 뉴스를 **한국어로** 작성하는 것이 임무입니다. "
        "절대로 영어로 작성하지 마세요. 모든 응답은 반드시 JSON 형식이어야 합니다."
    )
    writer_prompt = f"""
주제: '{cluster_topic}'

원본 기사 소스:
{context_text}

작업: 위 기사들을 종합하여 하나의 완결된 뉴스 기사를 **한국어로** 작성하세요.

필수 준수사항:
1. **팩트 기반**: 제공된 기사에 없는 내용은 절대 추가하지 마세요.
2. **한국어 작성**: 모든 내용은 반드시 한국어로 작성해야 합니다.
3. **구조**: 헤드라인 -> 리드 -> 본문 (원인/경과/세부사항) -> 결론
4. **중립성**: 감정적 표현 배제, 건조한 보도체 유지
5. **멀티미디어 언급 삭제**: "위 사진", "영상", "표" 등의 표현 제거

출력 JSON 형식:
{{
    "title": "한국어 헤드라인",
    "contents": "한국어로 작성된 전체 기사 본문",
    "search_keyword": "영문 검색어 (예: Samsung chip shortage)"
}}
"""
    
    draft_response = _call_llm(model_name, writer_system, writer_prompt, "json_object")
    draft_json = _safe_json_loads(draft_response)
    
    print(f"   📝 [Writer] 초안 생성: {draft_json.get('title', 'No Title')[:50]}")

    # ======================================================================================
    # Step 2: Critic Agent (Fact-Check & Review)
    # ======================================================================================
    critic_system = (
        "당신은 엄격한 편집장이자 팩트체커입니다. 기자가 작성한 초안을 원본 기사와 대조하여 검증하세요. "
        "할루시네이션, 누락, 편향이 있으면 FAIL, 완벽하면 PASS를 주세요. 응답은 JSON 형식입니다."
    )
    critic_prompt = f"""
원본 기사 소스:
{context_text}

기자 초안:
제목: {draft_json.get('title')}
내용: {draft_json.get('contents')}

평가 기준:
1. **할루시네이션**: 원본에 없는 내용을 지어냈는가?
2. **누락**: 중요한 날짜, 숫자, 인명이 빠졌는가?
3. **중립성**: 객관적인가?

출력 JSON 형식:
{{
    "status": "PASS" 또는 "FAIL",
    "feedback": "구체적인 수정 지시사항 (PASS면 비워두기)"
}}
"""
    
    critic_response = _call_llm(model_name, critic_system, critic_prompt, "json_object")
    critic_json = _safe_json_loads(critic_response)
    
    print(f"   🧐 [Critic] 평가: {critic_json.get('status')} - {critic_json.get('feedback', '')[:50]}")

    # ======================================================================================
    # Step 3: Editor Agent (Refine if needed)
    # ======================================================================================
    if critic_json.get("status") == "FAIL":
        editor_system = (
            "당신은 수석 편집자입니다. 비평가의 지적사항을 반영하여 기사를 수정하세요. "
            "모든 내용은 반드시 **한국어로** 작성해야 합니다. 응답은 JSON 형식입니다."
        )
        editor_prompt = f"""
수정할 초안:
제목: {draft_json.get('title')}
내용: {draft_json.get('contents')}
영문 키워드: {draft_json.get('search_keyword')}

비평가 피드백 (반드시 수정):
{critic_json.get('feedback')}

원본 기사 (참고용):
{context_text}

작업: 비평가의 피드백을 반영하여 기사를 다시 작성하세요.
**주의: 반드시 아래 JSON 형식을 정확히 지켜서 출력해야 합니다.**

출력 JSON 형식:
{{
    "title": "수정된 한국어 헤드라인",
    "contents": "수정된 전체 기사 본문",
    "search_keyword": "영문 검색어"
}}
"""
        
        final_response = _call_llm(model_name, editor_system, editor_prompt, "json_object")
        final_json = _safe_json_loads(final_response)
        
        # Double check if keys exist, if not try to recover or log raw
        if final_json.get("title") == "제목 없음":
             print(f"   ⚠️ [Editor] JSON 키 누락/파싱 실패. Raw Response: {final_response}")

        print(f"   ✅ [Editor] 수정 완료: {final_json.get('title', 'No Title')[:50]}")
        return final_json
    else:
        print(f"   ✅ [Agentic] 초안 승인: {draft_json.get('title', 'No Title')[:50]}")
        return draft_json

def _call_llm(model, system, user, format_type):
    try:
        response = openai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.2,
            response_format={"type": format_type}
        )
        content = response.choices[0].message.content
        # print(f"      [LLM] 응답 길이: {len(content)} chars")
        return content
    except Exception as e:
        print(f"   ⚠️ [LLM 오류]: {e}")
        return '{"title": "LLM 오류", "contents": "API 호출 실패", "search_keyword": ""}'

def _safe_json_loads(json_str):
    try:
        # 1. Markdown Code Block 제거 (```json ... ```)
        cleaned = json_str.strip()
        if cleaned.startswith("```"):
            # 첫 번째 줄 제거 (```json)
            parts = cleaned.split("\n", 1)
            if len(parts) > 1:
                cleaned = parts[1]
            # 마지막 줄 제거 (```)
            if cleaned.strip().endswith("```"):
                cleaned = cleaned.rsplit("```", 1)[0]
        
        result = json.loads(cleaned)
        
        # 2. 구조 평탄화 ( {"article": {...}} 형태 대응 )
        if "title" not in result and len(result) == 1:
            first_key = list(result.keys())[0]
            if isinstance(result[first_key], dict) and "title" in result[first_key]:
                result = result[first_key]

        # Ensure all required keys exist
        if "title" not in result:
            result["title"] = "제목 없음"
        if "contents" not in result:
            result["contents"] = "내용 생성 실패"
        if "search_keyword" not in result:
            result["search_keyword"] = ""
        return result
    except Exception as e:
        # 여기서 에러나면 Raw String을 반환하지 않고, 에러 객체를 반환하되 내용은 유지
        print(f"   ⚠️ [JSON 파싱 Exception]: {e}")
        return {"title": "JSON 파싱 오류", "contents": json_str, "search_keyword": ""}

