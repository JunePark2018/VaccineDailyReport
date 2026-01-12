import sys
from collections import defaultdict

# 만든 파일들 불러오기
from ai_helper import ask  
from ai_news_generator import NewsEditor 
from test_data import fake_articles_data

# AI 연결 어댑터
class AIAdapter:
    def __init__(self, model_name="gemini-2.5-flash"):
        self.model_name = model_name

    def ask(self, system_role, user_prompt):
        full_message = f"{system_role}\n\n[요청사항]\n{user_prompt}"
        return ask(self.model_name, full_message)

# 실행 함수
def run_generator():
    # 1. 어댑터 설정
    my_ai_adapter = AIAdapter(model_name="gemini-2.5-flash")
    
    # 2. 에디터 생성
    editor = NewsEditor(ai_helper=my_ai_adapter)

    # 3. 데이터 분류
    clusters = defaultdict(list)
    for article in fake_articles_data:
        clusters[article['category']].append(article)

    print(f"✅ {len(clusters)}개 카테고리 분류 완료.\n")

    # 4. 기사 생성
    for category, articles in clusters.items():
        print(f"✍️ Writing... [{category}] 분야 ({len(articles)}건)")
        
        final_article = editor.generate_balanced_article(category, articles)
        
        print("-" * 50)
        print(f"📰 [결과] {category} 뉴스")
        print("-" * 50)
        print(final_article)
        print("\n")

if __name__ == "__main__":
    run_generator()