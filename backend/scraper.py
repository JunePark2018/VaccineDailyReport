import requests
from bs4 import BeautifulSoup
import json
import time
import re


# 기사에 한글 비중이 25%이하면 무시합니다.
def is_korean_article(text, threshold=0.25):
    if not text:
        return False
    korean_chars = re.findall(r"[가-힣]", text)
    total_chars = len(text.replace(" ", ""))
    if total_chars == 0:
        return False
    return (len(korean_chars) / total_chars) >= threshold


def get_news_data(url):
    """
    [상세 페이지 파싱 함수]
    역할: 제목, 시간, 언론사, 카테고리, 기자, 본문, 이미지를 추출합니다.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        # 1. 기사 제목 및 언론사 추출
        title = (
            soup.select_one("h2#title_area span").get_text(strip=True)
            if soup.select_one("h2#title_area span")
            else "제목 없음"
        )
        company_name = (
            soup.select_one(".media_end_head_top_logo img")["title"]
            if soup.select_one(".media_end_head_top_logo img")
            else "언론사 미상"
        )

        # 네이버 뉴스 상단에 노출되는 섹션 정보(정치, 경제 등)를 가져옵니다.
        category_el = soup.select_one(".media_end_head_top_channel_layer_text strong")
        category = category_el.get_text(strip=True) if category_el else "미분류"

        # 2. 기사 시간 추출
        time_el = soup.select_one(".media_end_head_info_datestamp_time._ARTICLE_DATE_TIME")
        time_val = time_el["data-date-time"] if time_el and time_el.has_attr("data-date-time") else "시간 정보 없음"

        # 3. 본문 영역 확보 (기자명 추출을 위해 정제 전 원본 텍스트 보관 필요)
        content_area = soup.select_one("#newsct_article")
        if not content_area:
            return None
        raw_content_text = content_area.get_text(separator=" ", strip=True) if content_area else ""

        # 3-2 한글 필터링 적용
        if not is_korean_article(raw_content_text):
            return None

        # 4. [강화된 기자명 추출 로직]
        author = "기자 미상"

        # 4-1. 1순위: 네이버 표준 레이아웃(상단 기자명 영역) 탐색
        author_el = soup.select_one(".media_end_head_journalist_name")
        if author_el:
            author = author_el.get_text(strip=True)

        # 4-2. 2순위: 레이아웃에 없을 경우 본문 텍스트 내에서 패턴 매칭 (KBS, 연합뉴스 등 대응)
        if (author == "기자 미상" or not author) and raw_content_text:
            # 패턴 A: 이메일 앞의 이름 추출 (예: 홍길동 기자 abc@kbs.co.kr)
            email_match = re.search(r"([가-힣]{2,4})\s?(?:기자)?\s?[\w\.-]+@[\w\.-]+", raw_content_text)
            # 패턴 B: 본문 하단 'OOO 기자' 문구 추출
            name_match = re.search(r"([가-힣]{2,4})\s?기자", raw_content_text)

            if email_match:
                author = email_match.group(1).strip()
            elif name_match:
                author = name_match.group(1).strip()

        # 5. 이미지 URL 리스트 수집
        img_urls = [
            img.get("data-src") or img.get("src")
            for img in soup.select("#newsct_article img")
            if img.get("data-src") or img.get("src")
        ]

        # 6. 본문 텍스트 정제 (태그 제거)
        if content_area:
            # 원본 보존을 위해 copy를 사용하거나, 필요한 데이터를 뽑은 후 제거 진행
            for extra in content_area.select(".img_desc, .article_caption, em, script, style"):
                extra.decompose()
            contents = content_area.get_text(separator=" ", strip=True)
        else:
            contents = "내용 없음"

        return {
            "title": title,
            "time": time_val,  # 날짜
            "company_name": company_name,  # 언론사
            "author": author,  # 기자
            "contents": contents,  # 본문
            "img_urls": img_urls,  # 이미지
            "url": url,  # 링크
            "category": "미분류" # 카테고리는 run_article_crawler에서 줄 예정.
        }

    except Exception as e:
        print(f"[오류] 상세 페이지 파싱 실패: {url} | 사유: {e}")
        return None


def run_article_crawler(target_companies=None, debug_save=False, output_file="news_result.json"):
    """
    통합 크롤링 제어 함수.
    반환값: [get_news_data(url)가 반환한 값 리스트]

    섹션 100(정치) ~ 105(IT/과학)까지 순회하며 크롤링
    001:전체 100:정치, 101:경제, 102:사회, 103:생활/문화, 104:세계, 105:IT/과학
    """
    is_filter_mode = True if target_companies else False

    sections = ["100", "101", "102", "103", "104", "105"]
    section_names = {"100": "정치", "101": "경제", "102": "사회", "103": "생활", "104": "세계", "105": "IT"}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

    all_news_data = []
    # 중복 수집 방지를 위한 세트
    seen_urls = set()

    for sid in sections:
        print(f"\n[섹션 수집] {section_names[sid]} 뉴스 수집 중...")
        list_url = f"https://news.naver.com/main/list.naver?mode=LSD&mid=sec&sid1={sid}"

        try:
            response = requests.get(list_url, headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")

            # 목록에서 기사 URL 추출
            atags = soup.select(".list_body a, .sa_text_title")

            # 리스트 컴프리헨션으로 URL 정리 및 중복 제거
            urls = [a.get("href") for a in atags if a.get("href") and "article" in a.get("href")]

            for url in set(urls):  # 현재 섹션 내 중복 제거
                if url in seen_urls:
                    continue  # 이미 수집한 URL이면 패스

                data = get_news_data(url)
                if data:
                    # 만약 상세페이지에서 카테고리를 못 찾았을 때만 섹션 이름으로 채워줌
                    if data["category"] == "미분류":
                        data["category"] = section_names[sid]

                    if not target_companies or any(tc in data["company_name"] for tc in target_companies):
                        all_news_data.append(data)
                        seen_urls.add(url)
                        print(f"[수집] {data['company_name']} | {data['title'][:15]}...")

                time.sleep(0.1)  # 섹션 내 기사 간 휴식

        except Exception as e:
            print(f"[{sid}] 섹션 목록 수집 중 오류: {e}")
            continue

    return all_news_data
