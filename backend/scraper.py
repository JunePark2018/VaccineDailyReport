import requests
from bs4 import BeautifulSoup
import time
import re
from datetime import datetime, timedelta


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
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        title_el = soup.select_one("h2#title_area span")
        raw_title = title_el.get_text(strip=True) if title_el else "제목 없음"

        clean_title = re.sub(r"\[.*?\]|\(.*?\)|\<.*?\>", "", raw_title).strip()
        if not clean_title:
            clean_title = raw_title

        company_el = soup.select_one(".media_end_head_top_logo img")
        company_name = company_el["title"] if company_el else "언론사 미상"

        content_area = soup.select_one("#newsct_article")
        if not content_area:
            return None

        for extra in content_area.select(".img_desc, .article_caption, em, script, style, .sidebar, .ad"):
            extra.decompose()

        contents = content_area.get_text(separator=" ", strip=True)

        contents = re.sub(r"^[가-힣]{2,4}\s?=\s?[가-힣]{2,5}뉴스\)", "", contents)
        contents = re.sub(r"^[가-힣]{2,10}\s?뉴스", "", contents)
        contents = re.sub(r".*?기자\s?=", "", contents)

        contents = re.sub(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", "", contents)
        contents = re.sub(r"[^\w\s가-힣.?!,]", " ", contents)

        stop_phrases = ["무단전재", "재배포 금지", "저작권자", "Copyrights", "구독 신청", "관련기사", "제보하기"]
        for phrase in stop_phrases:
            if phrase in contents:
                contents = contents.split(phrase)[0].strip()

        contents = re.sub(r"\s+", " ", contents).strip()

        if not is_korean_article(contents):
            return None
        if len(contents) < 150:
            return None

        time_el = soup.select_one("._ARTICLE_DATE_TIME")
        time_str = time_el["data-date-time"] if time_el and time_el.has_attr("data-date-time") else "시간 정보 없음"

        return {
            "title": raw_title,
            "search_title": clean_title,
            "time": time_str,
            "company_name": company_name,
            "contents": contents,
            "img_urls": [img.get("data-src") or img.get("src") for img in soup.select("#newsct_article img")],
            "url": url,
            "category": "미분류",
        }

    except Exception as e:
        print(f"[오류] 파싱 실패: {url} | {e}")
        return None


def run_article_crawler(target_companies=None, days=7, max_pages=5):
    """
    최근 n일(days)치 뉴스 수집.
    - date=YYYYMMDD 로 하루치 목록을 긁어옴
    - 페이지가 있는 경우 page=1..max_pages 까지 순회
    """
    sections = ["100", "101", "102", "103", "104", "105"]
    section_names = {"100": "정치", "101": "경제", "102": "사회", "103": "생활/문화", "104": "세계", "105": "IT/과학"}

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

    all_news_data = []
    seen_urls = set()

    today = datetime.now()
    date_list = [(today - timedelta(days=i)).strftime("%Y%m%d") for i in range(days)]

    for sid in sections:
        print(f"\n[섹션 수집] {section_names[sid]} (최근 {days}일) 수집 중...")

        for ymd in date_list:
            for page in range(1, max_pages + 1):
                list_url = f"https://news.naver.com/main/list.naver?mode=LSD&mid=sec&sid1={sid}&date={ymd}&page={page}"

                try:
                    response = requests.get(list_url, headers=headers, timeout=10)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.text, "html.parser")

                    atags = soup.select(".list_body a, .sa_text_title")
                    urls = [a.get("href") for a in atags if a.get("href") and "article" in a.get("href")]
                    urls = list(set(urls))

                    # 해당 날짜/페이지에서 더 이상 뽑을 URL이 없으면 페이지 루프 중단
                    if not urls:
                        break

                    new_count = 0
                    for url in urls:
                        if url in seen_urls:
                            continue

                        data = get_news_data(url)
                        if data:
                            if data["category"] == "미분류":
                                data["category"] = section_names[sid]

                            if (not target_companies) or any(tc in data["company_name"] for tc in target_companies):
                                all_news_data.append(data)
                                seen_urls.add(url)
                                new_count += 1
                                print(f"[수집] {ymd} p{page} | {data['company_name']} | {data['title'][:15]}...")

                        time.sleep(0.1)

                    # “수집이 거의 안 되는 페이지”면 다음 페이지 의미가 적을 수 있어 조기 종료 옵션
                    # (원치 않으면 삭제해도 됨)
                    if new_count == 0 and page >= 2:
                        break

                except Exception as e:
                    print(f"[오류] sid={sid}, date={ymd}, page={page} | {e}")
                    break

    return all_news_data
