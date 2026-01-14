import random
import json
from datetime import datetime, timedelta

# Data for generation (Korean)
companies = [
    "OpenAI",
    "Google",
    "Samsung",
    "Apple",
    "Tesla",
    "NVIDIA",
    "Microsoft",
    "Meta",
    "Amazon",
    "SK Hynix",
    "Naver",
    "Kakao",
]
technologies = [
    "GPT-5",
    "양자 컴퓨터",
    "6G 네트워크",
    "전고체 배터리",
    "자율주행",
    "XR 글래스",
    "휴머노이드 로봇",
    "핵융합 에너지",
    "블록체인",
    "사이버 보안",
    "AI 반도체",
]
actions = ["공개", "발표", "개발", "투자", "인수", "출시", "제휴", "피소", "기록 경신", "경고"]
sectors = ["AI", "반도체", "바이오", "우주 항공", "자동차", "핀테크", "에너지", "로봇공학", "클라우드", "게임"]
adjectives = ["획기적인", "혁신적인", "논란의", "차세대", "고성능", "친환경", "글로벌", "대규모", "예상 밖의", "전략적"]

# Templates for titles and contents (Korean)
templates = [
    {
        "title": "{company}, {adjective} {tech} {action}... 업계 '지각변동' 예고",
        "content": "{company}가(이) {adjective} {tech} 기술을 전격 {action}했다. 전문가들은 이번 발표가 {sector} 산업의 판도를 뒤흔들 것이라고 분석했다. 발표 직후 {company}의 주가는 10% 이상 급등했다.",
        "keywords": ["{company}", "{tech}", "{sector}", "혁신"],
    },
    {
        "title": "{sector} 시장, {company}의 새로운 {tech}로 뜨거운 경쟁",
        "content": "글로벌 {sector} 시장이 {company}의 {tech} 등장으로 격변하고 있다. 경쟁사들과의 치열한 기술 경쟁이 예상된다. 업계 관계자는 '이는 게임 체인저가 될 것'이라고 평가했다.",
        "keywords": ["{sector}", "{tech}", "{company}", "시장 동향"],
    },
    {
        "title": "왜 {company}의 {tech}에 주목해야 하는가",
        "content": "{company}는 최근 컨퍼런스에서 {tech}의 놀라운 성능을 시연했다. 기존 모델 대비 효율이 50% 향상되었다. 이로써 {company}는 {sector} 분야에서의 리더십을 더욱 공고히 했다.",
        "keywords": ["{company}", "{tech}", "효율성", "{sector}"],
    },
    {
        "title": "{tech} 급성장에 정부 규제 강화... {sector} 업계 우려",
        "content": "{tech} 기술이 급속도로 발전함에 따라 규제 당국이 칼을 빼들었다. {company} 측은 과도한 규제가 {sector} 분야의 혁신을 저해할 수 있다며 우려를 표명했다. 다음 달 관련 공청회가 열릴 예정이다.",
        "keywords": ["규제", "{sector}", "{tech}", "정책"],
    },
    {
        "title": "투자자들, {tech} 리더 {company}에 '러브콜'",
        "content": "월가는 {tech} 분야에서 앞서가는 {company}에 매수 의견을 유지하고 있다. 헤지펀드들은 내년 매출이 두 배로 성장할 것으로 기대하며 지분을 늘리고 있다. {sector} 붐은 당분간 지속될 전망이다.",
        "keywords": ["투자", "{company}", "{tech}", "주식"],
    },
]


def generate_article(index):
    company = random.choice(companies)
    tech = random.choice(technologies)
    action = random.choice(actions)
    sector = random.choice(sectors)
    adjective = random.choice(adjectives)

    template = random.choice(templates)

    title = template["title"].format(company=company, action=action, adjective=adjective, tech=tech, sector=sector)
    content = template["content"].format(company=company, action=action, adjective=adjective, tech=tech, sector=sector)

    # Simple keyword replacement for the template keywords
    keywords = [k.format(company=company, tech=tech, sector=sector) for k in template["keywords"]]

    # Random sentiment and score
    sentiment = random.choice(["positive", "neutral", "negative"])
    score = random.randint(10, 99)

    analysis_result = {"summary": title, "keywords": keywords, "sentiment": sentiment, "score": score}

    # Random time within last 30 days
    days_ago = random.randint(0, 30)
    hours_ago = random.randint(0, 23)
    random_date = datetime.now() - timedelta(days=days_ago, hours=hours_ago)
    random_date_str = random_date.strftime("%Y-%m-%d %H:%M:%S")

    return f"""(
    '{title.replace("'", "''")}',
    '{content.replace("'", "''")}',
    '{json.dumps(analysis_result, ensure_ascii=False).replace("'", "''")}',
    '{random_date_str}'
)"""


# Generate 100 articles
entries = []
for i in range(100):
    entries.append(generate_article(i))

# Create the SQL content
sql_content = "-- 임시용 Issue 데이터 생성기입니다.\n\nDELETE FROM issues;\n\nINSERT INTO issues (title, contents, analysis_result, created_at) VALUES \n"
sql_content += ",\n".join(entries)
sql_content += ";"

# Write to file
# Force UTF-8 encoding for Korean characters
with open(r"c:\Users\201-03\PycharmProjects\FinalProject\backend\init.sql", "w", encoding="utf-8") as f:
    f.write(sql_content)

print("Successfully generated init.sql with 100 Korean articles.")
