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
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        # 1. 기사 제목 추출 및 정제
        title_el = soup.select_one("h2#title_area span")
        raw_title = title_el.get_text(strip=True) if title_el else "제목 없음"
        
        # [추가] 제목 정제 로직: [속보], (상보), <단독> 등 제거
        # 분석 성능을 높이기 위해 특수기호 안의 텍스트를 삭제합니다.
        clean_title = re.sub(r'\[.*?\]|\(.*?\)|\<.*?\>', '', raw_title).strip()
        # 만약 정제 후 제목이 비어버리면 원본 사용
        if not clean_title:
            clean_title = raw_title

        # 언론사 추출
        company_el = soup.select_one(".media_end_head_top_logo img")
        company_name = company_el["title"] if company_el else "언론사 미상"

        # 2. 본문 영역 확보
        content_area = soup.select_one("#newsct_article")
        if not content_area:
            return None

        for extra in content_area.select(".img_desc, .article_caption, em, script, style, .sidebar, .ad"):
            extra.decompose()

        contents = content_area.get_text(separator=" ", strip=True)

        # ---------------------------------------------------------
        # [본문 정제 로직 - 기존 유지 및 강화]
        # ---------------------------------------------------------
        contents = re.sub(r'^[가-힣]{2,4}\s?=\s?[가-힣]{2,5}뉴스\)', '', contents)
        contents = re.sub(r'^[가-힣]{2,10}\s?뉴스', '', contents)
        contents = re.sub(r'.*?기자\s?=', '', contents)

        contents = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '', contents)
        contents = re.sub(r'[^\w\s가-힣.?!,]', ' ', contents)

        stop_phrases = ["무단전재", "재배포 금지", "저작권자", "Copyrights", "구독 신청", "관련기사", "제보하기"]
        for phrase in stop_phrases:
            if phrase in contents:
                contents = contents.split(phrase)[0].strip()

        contents = re.sub(r'\s+', ' ', contents).strip()

        if not is_korean_article(contents):
            return None

        if len(contents) < 150:
            return None

        return {
            "title": raw_title,        # 화면 표시용 원본 제목
            "search_title": clean_title, # AI 분석/임베딩용 정제 제목 (추천)
            "time": (soup.select_one("._ARTICLE_DATE_TIME")["data-date-time"] if soup.select_one("._ARTICLE_DATE_TIME") else "시간 정보 없음"),
            "company_name": company_name,
            "contents": contents,
            "img_urls": [img.get("data-src") or img.get("src") for img in soup.select("#newsct_article img")],
            "url": url,
            "category": "미분류"
        }

    except Exception as e:
        print(f"[오류] 파싱 실패: {url} | {e}")
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
    section_names = {"100": "정치", "101": "경제", "102": "사회", "103": "생활/문화", "104": "세계", "105": "IT/과학"}
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
