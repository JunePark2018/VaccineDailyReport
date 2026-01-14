import math
import re
from collections import Counter
from ai_helper import ask

# ==============================================================================
# [보조 함수 1] 기사들의 핵심 키워드 추출 (군집 중심성 판단용)
# ==============================================================================
def get_cluster_keywords(articles):
    """
    전체 기사 내용을 분석하여 가장 많이 등장하는 '핵심 단어' 상위 20개를 추출합니다.
    (이 단어들을 많이 포함한 기사가 '주제를 잘 대표하는 기사'라고 판단하기 위함)
    """
    all_text = " ".join([art['contents'] for art in articles])
    # 한글, 영어, 숫자만 남기고 특수문자 제거
    cleaned_text = re.sub(r'[^\w\s]', '', all_text)
    words = cleaned_text.split()
    
    # 2글자 이상인 단어만 카운트 (조사 '은/는/이/가' 등 제외 목적)
    meaningful_words = [w for w in words if len(w) >= 2]
    
    # 빈도수 계산
    count = Counter(meaningful_words)
    
    # 상위 20개 단어 리스트 반환
    return [word for word, cnt in count.most_common(20)]

# ==============================================================================
# [보조 함수 2] 기사별 품질 점수 계산 (고급 스코어링)
# ==============================================================================
def calculate_advanced_score(article, cluster_keywords):
    """
    기사의 가치를 4가지 기준으로 평가하여 점수(0~100점)를 매깁니다.
    
    1. 정보 밀도 (30%): 따옴표("), 숫자(123)가 많을수록 팩트가 풍부함
    2. 제목 건전성 (20%): '충격', '경악' 같은 낚시성 제목 감점 / '종합', '분석' 가산점
    3. 군집 대표성 (30%): 전체 핵심 키워드를 얼마나 많이 포함하고 있는지
    4. 본문 길이 (20%): 너무 짧은 기사는 정보 부족으로 간주
    """
    
    # 1. [정보 밀도] (가중치 30%)
    quote_count = article['contents'].count('"') + article['contents'].count("'")
    digit_count = sum(c.isdigit() for c in article['contents'])
    density_score = min(100, (quote_count * 1.5) + (digit_count * 0.5))

    # 2. [제목 건전성] (가중치 20%)
    title = article['title']
    title_score = 50 # 기본점수

    # 감점 요인 (낚시성 키워드)
    bad_keywords = ["충격", "경악", "속보", "헉", "결국", "...", "?!"]
    if any(k in title for k in bad_keywords):
        title_score -= 30
    
    # 가산 요인 (정리형 키워드)
    good_keywords = ["종합", "분석", "정리", "이유", "배경", "전망", "팩트"]
    if any(k in title for k in good_keywords):
        title_score += 30
        
    title_score = max(0, min(100, title_score))

    # 3. [군집 대표성] (가중치 30%)
    content_words = set(article['contents'].split())
    match_count = sum(1 for keyword in cluster_keywords if keyword in content_words)
    centrality_score = min(100, match_count * 10) # 키워드 10개 이상 포함시 만점

    # 4. [본문 길이] (가중치 20%)
    length = len(article['contents'])
    length_score = min(100, math.log(length + 1) * 15) if length > 0 else 0

    # [최종 합산]
    final_score = (centrality_score * 0.3) + \
                  (density_score * 0.3) + \
                  (title_score * 0.2) + \
                  (length_score * 0.2)
                  
    return final_score


# ==============================================================================
# [메인 함수] 기사 생성기
# ==============================================================================
def generate_balanced_article(model_name, cluster_topic, articles):
    """
    =============================================================================
    [함수 설명]
    여러 개의 개별 기사(Source Articles)를 AI가 분석하고 종합하여,
    하나의 완결된 고품질 '스트레이트 뉴스'로 재작성하는 함수입니다.
    =============================================================================

    [작동 원리]
    1. 선별: '고급 스코어링' 알고리즘으로 가장 영양가 있는 상위 10개 기사를 뽑습니다.
    2. 전처리: 선별된 기사들을 AI가 읽기 좋게 하나의 텍스트로 합칩니다.
    3. 설정: AI에게 '수석 편집장' 페르소나를 부여하고, 엄격한 보도 지침을 내립니다.
    4. 생성: AI 모델(Gemini/GPT 등)에 작성을 요청하고 결과를 받아옵니다.

    [입력 파라미터 (Parameters)]
    1. model_name (str)
       - 사용할 AI 모델의 이름 (예: "gemini-1.5-flash", "gpt-4o")
    
    2. cluster_topic (str)
       - 기사들의 공통 주제 (예: "IT/과학", "경제/반도체")
    
    3. articles (list)
       - 기사 정보가 담긴 딕셔너리(Dictionary)들의 리스트입니다.
       - 각 딕셔너리는 반드시 다음 3가지 키(Key)를 포함해야 합니다:
         * 'company_name': 언론사 이름
         * 'title': 기사 제목
         * 'contents': 기사 본문 내용

    [출력 리턴값 (Returns)]
    - type: str (문자열)
    - 내용: AI가 작성을 완료한 최종 기사 (헤드라인 + 본문 포함)
    =============================================================================
    """

    # 0. 예외 처리: 기사가 하나도 없으면 빈 문자열 반환
    if not articles:
        return ""

    # ------------------------------------------------------------------
    # [1단계: 스마트 데이터 선별 (Smart Data Pruning)]
    # 기사가 너무 많으면 AI 성능이 떨어지므로, '품질 점수'가 높은 상위 10개만 뽑습니다.
    # ------------------------------------------------------------------
    
    # 1-1. 전체 기사를 관통하는 핵심 키워드 추출
    top_keywords = get_cluster_keywords(articles)

    # 1-2. 각 기사별 품질 점수(Score) 계산
    scored_articles = []
    for art in articles:
        score = calculate_advanced_score(art, top_keywords)
        scored_articles.append((score, art))

    # 1-3. 점수 높은 순서대로 정렬 (내림차순)
    scored_articles.sort(key=lambda x: x[0], reverse=True)

    # 1-4. 상위 10개(Top 10)만 선택
    target_articles = [item[1] for item in scored_articles[:10]]

    # (디버깅용: 터미널에서 선별 결과 확인)
    print(f"   📊 [스마트 선별 완료] 전체 {len(articles)}개 중 상위 {len(target_articles)}개 엄선")
    print(f"      - 1위 기사: {target_articles[0]['title']} (점수: {scored_articles[0][0]:.1f})")

    # ------------------------------------------------------------------
    # [2단계: 기사 내용 합치기 (Context Building)]
    # ------------------------------------------------------------------
    context_text = ""
    for idx, art in enumerate(target_articles):
        # 날짜 포맷팅 (datetime 객체인 경우 문자열로 변환)
        date_str = art['time'].strftime('%Y-%m-%d %H:%M') if 'time' in art else "Unknown"
        
        context_text += (
            f"[{idx+1}] 보도일시: {date_str} | 언론사: {art['company_name']}\n"
            f"    제목: {art['title']}\n"
            f"    내용: {art['contents']}\n\n"
        )

    # ------------------------------------------------------------------
    # [3단계: 프롬프트 작성 (Prompt Engineering)]
    # ------------------------------------------------------------------
    
    # 시스템 프롬프트 (역할 부여)
    system_role = (
        "당신은 중복 없이 간결하고 명확한 문장을 구사하며, 팩트 검증에 철저한 '수석 편집장'입니다. "
        "여러 기사를 읽고, 독자가 한 번에 이해할 수 있도록 내용을 재구성하십시오."
        "단순 요약이 아니라, 사건의 인과관계를 완벽히 파악하여 하나의 완성된 기사를 써야 합니다."
    )

    # 유저 프롬프트 (작성 가이드라인)
    user_prompt = f"""
        주제: '{cluster_topic}'
        
        아래 제공된 기사 소스들을 바탕으로 **하나의 완결된 스트레이트 뉴스**를 작성하세요.
        (참고: 제공된 소스는 전체 데이터 중 가장 가치가 높은 기사들을 선별한 것입니다.)

        [수집된 기사 소스]
        {context_text}

        [🚨 작성 절대 원칙 - 어길 시 해고]
        1. **팩트 준수 (Fact-Only)**: 소스에 없는 내용은 절대 창작하거나 추측하지 마십시오.
        2. **중복 금지**: 같은 내용을 단어만 바꿔 반복하지 마십시오.
        3. **문체 및 어조 (Tone & Style)**:
           - 반드시 **'~다', '~했다'** 등의 건조한 신문 기사체(하라체)를 사용하십시오. ('~입니다' 절대 금지)
           - '충격', '경악' 같은 감정적 수식어를 배제하고 객관적인 서술을 유지하십시오.
           - '한편', '결론적으로' 같은 상투적인 에세이식 접속사 사용을 최소화하십시오.
        4. **논리적 흐름**:
           - **인용구 활용**: 현장감을 살리기 위해 관계자의 핵심 발언은 요약하지 말고 **큰따옴표(" ")**를 사용해 직접 인용하십시오.
           - [서론 -> 본론 -> 결론]의 논리적 흐름을 갖추되, 목차(서론, 본론 등)를 텍스트로 적지는 마십시오.

        [기사 구조 가이드라인]
        1. **헤드라인**: 전체를 아우르는 30자 이내의 제목 (1개)
        2. **리드(서두)**: 첫 문단만 읽어도 핵심(누가, 무엇을, 왜) 파악 가능하도록 요약
        3. **본문**: 
           - 중복 팩트 병합
           - 시간 순서 및 인과 관계에 따른 배치
           - 출처 나열 지양 ("A에 따르면..." 반복 금지)
        4. **마무리**: 향후 전망이나 업계 반응
        5. **분량 제한**: 전체 기사는 공백 포함 **최대 4000자 이내**로 작성하여, 문장이 중간에 잘리지 않도록 핵심 위주로 압축하십시오.

        위 가이드라인을 철저히 지켜 기사를 작성해 주세요.
    """

    # ------------------------------------------------------------------
    # [4단계: AI 요청 및 결과 반환]
    # ------------------------------------------------------------------
    full_message = f"{system_role}\n\n[요청사항]\n{user_prompt}"
    return ask(model_name, full_message)