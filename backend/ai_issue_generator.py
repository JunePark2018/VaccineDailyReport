import os
import re
import json
from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()

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

    # 2) 시스템 프롬프트 (역할 부여)
    system_role = (
        "당신은 중복 없이 간결하고 명확한 문장을 구사하며, 팩트 검증에 철저한 '수석 편집장'입니다. "
        "여러 기사를 읽고, 독자가 한 번에 이해할 수 있도록 내용을 재구성하십시오." \
        "당신의 응답은 반드시 프로그래밍적으로 파싱 가능한 **정확한 JSON 형식**이어야 합니다."
    )

    # 3) 유저 프롬프트 (팩트 준수 원칙 추가)
    user_prompt = f"""
주제: '{cluster_topic}'

아래 제공된 기사 소스들을 바탕으로 **하나의 완결된 스트레이트 뉴스**를 작성하세요.
추가로 이 사건에 대한 해외 외신 반응을 추적하기 위한 영문 검색어도 추출하십시오.

[수집된 기사 소스]
{context_text}

[🚨 작성 절대 원칙 - 어길 시 해고]
1. **팩트 준수 (Fact-Only)**: 제공된 기사 소스에 없는 내용은 절대 창작하거나 추측하여 쓰지 마십시오. 오직 주어진 텍스트 데이터에 기반해서만 서술해야 합니다. (없는 내용은 아예 언급하지 말 것)
2. **중복 금지**: 앞에서 언급한 문장이나 단락을 절대 다시 쓰지 마십시오. 똑같은 내용을 단어만 바꿔서 반복하는 것도 금지합니다.
3. **객관성 유지**: 감정적인 형용사나 과장된 표현을 배제하고, 건조하고 전문적인 보도체를 유지하십시오.
4. **논리적 흐름**: [서론 -> 본론 -> 결론]의 흐름이 끊기지 않고 자연스럽게 이어지도록 하십시오.

[기사 구조 가이드라인]
1. **헤드라인**: 전체를 아우르는 30자 이내의 제목 (단 1개만 작성)
2. **리드(서두)**: 첫 문단만 읽어도 핵심(누가, 무엇을, 왜)을 알 수 있게 요약하십시오.
3. **본문**:
   - 반복되는 팩트는 하나로 합치십시오.
   - 시간 순서나 인과 관계(원인->결과)에 따라 내용을 배치하십시오.
   - "A에 따르면", "B에 따르면" 같은 출처 나열을 피하고 사건 중심으로 서술하십시오.
4. **마무리**: 향후 전망이나 업계 반응으로 끝맺음하십시오.
5. 추가로 영문 검색어 추출: 이 사건이 해외 언론(Google News)에서 보도될 때 사용될 법한 핵심 영문 키워드 1개를 생성하십시오. (예: 'Samsung earnings shock', 'South Korea ferry incident') 

[출력 형식 가이드 - 반드시 아래 JSON 구조를 지킬 것]
{{
    "title": "헤드라인 제목",
    "contents": "작성된 전체 기사 본문 내용 (마크다운 형식 권장)",
    "search_keyword": "추출된 영문 검색어"
}}

위 가이드라인을 철저히 지켜 기사를 작성해 주세요.
""".strip()

    # 4) AI에게 요청 (ask를 여기로 흡수)
    try:
        response = openai_client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_role},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
            max_tokens=4000,
            top_p=0.9,
            frequency_penalty=0.5,
            response_format={"type": "json_object"}
        )
        raw_response = response.choices[0].message.content or "{}"
        try:
            result = json.loads(raw_response)
            # 필수 키가 없는 경우 대비
            if "contents" not in result: result["contents"] = str(raw_response)
            if "search_keyword" not in result: result["search_keyword"] = ""
            if "title" not in result: result["title"] = f"{cluster_topic} 이슈"
            
            return result
            
        except json.JSONDecodeError:
            print(f"❌ JSON 파싱 실패. Raw: {raw_response[:100]}...")
            # 마크다운 코드블록 제거 후 재시도
            clean_json = raw_response.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_json)

    except Exception as e:
        print(f"⚠️ 에러 발생: {str(e)}")
        return {
            "title": "생성 실패",
            "contents": f"AI 처리 중 오류가 발생했습니다: {str(e)}",
            "search_keyword": ""
        }