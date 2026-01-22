# scraper.py
import requests
from bs4 import BeautifulSoup
import re
import time
from datetime import datetime, timedelta
from sqlalchemy import and_
from database.models import News, Company


# ---------------------------------------------------------
# 1. 유틸리티 함수
# ---------------------------------------------------------
def is_korean_article(text, threshold=0.25):
    if not text:
        return False
    korean_chars = re.findall(r"[가-힣]", text)
    total_chars = len(text.replace(" ", ""))
    if total_chars == 0:
        return False
    return (len(korean_chars) / total_chars) >= threshold


def get_news_data(url):
    # [설정] 네이버 차단을 피하기 위한 헤더
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        title_el = soup.select_one("h2#title_area span")
        raw_title = title_el.get_text(strip=True) if title_el else "제목 없음"

        content_area = soup.select_one("#newsct_article")
        if not content_area:
            return None

        for extra in content_area.select(".img_desc, .article_caption, em, script, style, .sidebar, .ad"):
            extra.decompose()

        contents = content_area.get_text(separator=" ", strip=True)

        # 본문 정제 로직
        contents = re.sub(r"^[가-힣]{2,4}\s?=\s?[가-힣]{2,5}뉴스\)", "", contents)
        contents = re.sub(r".*?기자\s?=", "", contents)
        contents = re.sub(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", "", contents)
        contents = re.sub(r"[^\w\s가-힣.?!,]", " ", contents)

        stop_phrases = ["무단전재", "재배포 금지", "저작권자", "Copyrights"]
        for phrase in stop_phrases:
            if phrase in contents:
                contents = contents.split(phrase)[0].strip()

        contents = re.sub(r"\s+", " ", contents).strip()

        if not is_korean_article(contents) or len(contents) < 200:
            return None

        # 이미지 URL 추출
        img_urls = [img.get("data-src") or img.get("src") for img in soup.select("#newsct_article img")]

        return {
            "title": raw_title,
            "contents": contents,
            "time": (
                soup.select_one("._ARTICLE_DATE_TIME")["data-date-time"]
                if soup.select_one("._ARTICLE_DATE_TIME")
                else "시간 정보 없음"
            ),
            "company_name": (
                soup.select_one(".media_end_head_top_logo img")["title"]
                if soup.select_one(".media_end_head_top_logo img")
                else "언론사 미상"
            ),
            "img_urls": img_urls,
            "url": url,
            "category": "미분류",  # 기본값 설정
        }
    except Exception as e:
        # print(f"파싱 에러: {e}")
        return None


# ---------------------------------------------------------
# 2. 메인 크롤러 (작성하신 DB 체크 버전)
# ---------------------------------------------------------
def run_article_crawler(db_session, target_companies=None):
    """
    1. URL 중복 체크
    2. 메모리 내 제목 중복 체크 (함수 실행 중 중복 방지)
    3. DB 내 제목+언론사 중복 체크 (카테고리 꼼수 방지)
    """
    sections = ["100", "101", "102", "103", "104", "105"]
    section_names = {"100": "정치", "101": "경제", "102": "사회", "103": "생활/문화", "104": "세계", "105": "IT/과학"}
    new_news_list = []

    # 메모리 중복 체크용 변수 초기화
    collected_titles = set()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

    for sid in sections:
        print(f"\n--- [{section_names[sid]}] 섹션 스캔 중... ---")
        list_url = f"https://news.naver.com/main/list.naver?mode=LSD&mid=sec&sid1={sid}"

        try:
            res = requests.get(list_url, headers=headers, timeout=10)
            soup = BeautifulSoup(res.text, "html.parser")

            atags = soup.select(".list_body a, .sa_text_title")
            # URL 리스트 확보
            urls = list(set([a.get("href") for a in atags if a.get("href") and "article" in a.get("href")]))

            for url in urls:
                # 1. DB URL 중복 체크 (가장 빠름)
                if db_session.query(News.id).filter(News.url == url).first():
                    continue

                data = get_news_data(url)
                if not data:
                    continue

                # 2. 제목 정제 및 키 생성
                clean_title = data["title"].strip()
                title_key = (data["company_name"], clean_title)

                # [메모리 체크] 이번 실행 중에 이미 수집했는지 확인
                if title_key in collected_titles:
                    print(f"  [SKIP] 메모리 중복: {clean_title[:20]}...")
                    continue

                # [DB 체크] 기존 DB에 언론사 + 제목이 같은 기사가 있는지 확인
                exists_content = (
                    db_session.query(News)
                    .join(Company)
                    .filter(News.title == data["title"], Company.name == data["company_name"])
                    .first()
                )

                if exists_content:
                    print(f"  [SKIP] DB 내용 중복: {clean_title[:20]}...")
                    collected_titles.add(title_key)
                    continue

                # 3. 언론사 필터링
                if target_companies:
                    if not any(tc in data["company_name"] for tc in target_companies):
                        continue

                # 수집 성공 처리
                print(f"  ✅ [NEW] {data['company_name']} | {clean_title[:30]}...")
                collected_titles.add(title_key)

                # 섹션 정보 주입
                data["category"] = section_names[sid]
                new_news_list.append(data)

                time.sleep(0.1)

        except Exception as e:
            print(f"  ❌ [{sid}] 섹션 오류: {e}")
            continue

    return new_news_list


def crawl_n_days(
    db_session,  # [수정] DB 세션 필수 추가
    n_days: int,
    sections=("100", "101", "102", "103", "104", "105"),
    pages_per_day=5,
    target_companies=None,
    sleep_sec=0.1,
):
    """
    네이버 뉴스 '목록'을 날짜(date=YYYYMMDD)와 페이지(page=)로 확장해서 n일치 기사 수집.
    [필수] db_session: 중복 체크를 위한 DB 세션
    """
    section_names = {
        "100": "정치",
        "101": "경제",
        "102": "사회",
        "103": "생활/문화",
        "104": "세계",
        "105": "IT/과학",
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

    all_news_data = []

    # [수정] 메모리 중복 방지 (이번 실행 텀에서 중복 방지)
    collected_titles = set()

    today = datetime.now()

    for d in range(n_days):
        day = today - timedelta(days=d)
        ymd = day.strftime("%Y%m%d")
        print(f"\n📅 [날짜 수집] {ymd} (D-{d})")

        for sid in sections:
            print(f"   └─ [{section_names.get(sid, sid)}] 섹션 스캔 중...")

            for page in range(1, pages_per_day + 1):
                list_url = (
                    "https://news.naver.com/main/list.naver" f"?mode=LSD&mid=sec&sid1={sid}&date={ymd}&page={page}"
                )

                try:
                    resp = requests.get(list_url, headers=headers, timeout=10)
                    resp.raise_for_status()
                    soup = BeautifulSoup(resp.text, "html.parser")

                    # 목록에서 기사 URL 추출
                    atags = soup.select(".list_body a, .sa_text_title, a[href*='article']")
                    urls = [a.get("href") for a in atags if a.get("href") and "article" in a.get("href")]

                    if not urls:
                        break

                    for url in set(urls):
                        # ---------------------------------------------------------
                        # 1. DB URL 중복 체크 (run_article_crawler와 로직 통일)
                        # ---------------------------------------------------------
                        if db_session.query(News.id).filter(News.url == url).first():
                            # print(f"     [PASS] 이미 수집된 URL")
                            continue

                        data = get_news_data(url)  # 상세 파싱
                        if not data:
                            continue

                        # ---------------------------------------------------------
                        # 2. 제목+언론사 중복 체크 (메모리 + DB)
                        # ---------------------------------------------------------
                        clean_title = data["title"].strip()
                        title_key = (data["company_name"], clean_title)

                        # [메모리 체크]
                        if title_key in collected_titles:
                            continue

                        # [DB 정밀 체크]
                        exists_content = (
                            db_session.query(News)
                            .join(Company)
                            .filter(News.title == data["title"], Company.name == data["company_name"])
                            .first()
                        )

                        if exists_content:
                            collected_titles.add(title_key)
                            continue

                        # ---------------------------------------------------------
                        # 3. 필터링 및 데이터 처리
                        # ---------------------------------------------------------
                        if data.get("category") == "미분류":
                            data["category"] = section_names.get(sid, "미분류")

                        if target_companies and not any(tc in data["company_name"] for tc in target_companies):
                            continue

                        # 수집 성공
                        all_news_data.append(data)
                        collected_titles.add(title_key)
                        print(f"     ✅ [GET] {data['company_name']} | {data['title'][:20]}...")

                        time.sleep(sleep_sec)

                except Exception as e:
                    print(f"     ❌ [오류] {ymd} sid={sid} page={page} | {e}")
                    continue

    return all_news_data
