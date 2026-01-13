import sys
import time
from collections import defaultdict

# 만든 파일들 불러오기
# (만약 여기서 에러가 나면 ai_helper.py 파일 문제일 확률이 높습니다)
from ai_issue_generator import generate_balanced_article
from test_data import fake_articles_data


# =========================================================
# 실행 함수
# =========================================================
def run_generator():
    # [설정] 모델 선택
    target_model = "gemini-2.5-flash"

    # [설정] 재시도 횟수
    MAX_RETRIES = 3

    print(f"🚀 뉴스 생성 시스템 시작 (Model: {target_model})")

    # 2. 데이터 분류
    clusters = defaultdict(list)
    for article in fake_articles_data:
        clusters[article["category"]].append(article)

    print(f"✅ {len(clusters)}개 카테고리 분류 완료.\n")

    # 3. 기사 생성 및 화면 출력
    for category, articles in clusters.items():
        print(f"✍️  Writing... [{category}] 분야 ({len(articles)}건 통합 중)")

        final_article = ""

        # 재시도 로직
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                final_article = generate_balanced_article(target_model, category, articles)

                # 성공 시 (내용 있고, 경고 아이콘 없음)
                if final_article and "⚠️" not in final_article:
                    break

                # 실패 시
                print(f"   ⚠️ 시도 {attempt}/{MAX_RETRIES} 실패... (잠시 대기)")
                time.sleep(2)

            except Exception as e:
                print(f"   ⚠️ 에러 발생: {e}")
                time.sleep(2)

        # 결과 화면 출력
        print("\n" + "=" * 60)
        print(f"📰  [AI 완성 기사] {category}")
        print("=" * 60)

        if final_article and "⚠️" not in final_article:
            print(final_article)
        else:
            # 실패했다면 마지막 에러 메시지라도 출력
            print(f"⚠️  기사 생성 실패: {final_article}")

        print("\n" + ("-" * 60) + "\n")

    print("🏁 모든 작업이 완료되었습니다.")


if __name__ == "__main__":
    run_generator()
