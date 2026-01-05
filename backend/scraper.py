import requests
from bs4 import BeautifulSoup
import json
import time
import re


def get_news_data(url):
    """
    [상세 페이지 파싱 함수]
    역할: 제목, 시간, 언론사, 기자(강화된 로직), 본문, 이미지를 추출합니다.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # 1. 기사 제목 및 언론사 추출
        title = soup.select_one('h2#title_area span').get_text(strip=True) if soup.select_one(
            'h2#title_area span') else "제목 없음"
        company_name = soup.select_one('.media_end_head_top_logo img')['title'] if soup.select_one(
            '.media_end_head_top_logo img') else "언론사 미상"

        # 2. 기사 시간 추출
        time_el = soup.select_one('.media_end_head_info_datestamp_time._ARTICLE_DATE_TIME')
        time_val = time_el['data-date-time'] if time_el and time_el.has_attr('data-date-time') else "시간 정보 없음"

        # 3. 본문 영역 확보 (기자명 추출을 위해 정제 전 원본 텍스트 보관 필요)
        content_area = soup.select_one('#newsct_article')
        raw_content_text = content_area.get_text(separator=' ', strip=True) if content_area else ""

        # 4. [강화된 기자명 추출 로직]
        author = "기자 미상"

        # 4-1. 1순위: 네이버 표준 레이아웃(상단 기자명 영역) 탐색
        author_el = soup.select_one('.media_end_head_journalist_name')
        if author_el:
            author = author_el.get_text(strip=True)

        # 4-2. 2순위: 레이아웃에 없을 경우 본문 텍스트 내에서 패턴 매칭 (KBS, 연합뉴스 등 대응)
        if (author == "기자 미상" or not author) and raw_content_text:
            # 패턴 A: 이메일 앞의 이름 추출 (예: 홍길동 기자 abc@kbs.co.kr)
            email_match = re.search(r'([가-힣]{2,4})\s?(?:기자)?\s?[\w\.-]+@[\w\.-]+', raw_content_text)
            # 패턴 B: 본문 하단 'OOO 기자' 문구 추출
            name_match = re.search(r'([가-힣]{2,4})\s?기자', raw_content_text)

            if email_match:
                author = email_match.group(1).strip()
            elif name_match:
                author = name_match.group(1).strip()

        # 5. 이미지 URL 리스트 수집
        img_urls = [img.get('data-src') or img.get('src') for img in soup.select('#newsct_article img') if
                    img.get('data-src') or img.get('src')]

        # 6. 본문 텍스트 정제 (태그 제거)
        if content_area:
            # 원본 보존을 위해 copy를 사용하거나, 필요한 데이터를 뽑은 후 제거 진행
            for extra in content_area.select('.img_desc, .article_caption, em, script, style'):
                extra.decompose()
            contents = content_area.get_text(separator=' ', strip=True)
        else:
            contents = "내용 없음"

        return {
            "title": title,
            "time": time_val,
            "company_name": company_name,
            "author": author,
            "contents": contents,
            "img_url": img_urls,
            "url": url
        }

    except Exception as e:
        print(f"[오류] 상세 페이지 파싱 실패: {url} | 사유: {e}")
        return None


def run_article_crawler(target_companies=None, debug_save=True, output_file='news_result.json'):
    """
    통합 크롤링 제어 함수.
    반환값:
    [
        {
            "title": title,
            "time": time_val,
            "company_name": company_name,
            "author": author,
            "contents": contents,
            "img_url": img_urls,
            "url": url
        },
        ...
    ]
    """
    is_filter_mode = True if target_companies else False
    list_url = "https://news.naver.com/main/list.naver?mode=LSD&mid=sec&sid1=001"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"}

    news_list_data = []

    try:
        print(f"[시스템] 뉴스 목록 분석 중...")
        response = requests.get(list_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        atags = soup.select('.list_body a, .sa_text_title')
        urls = list(set([a.get('href') for a in atags if a.get('href') and 'article' in a.get('href')]))

        print(f"[시스템] 총 {len(urls)}개의 최신 기사 후보 발견.")

        for url in urls:
            data = get_news_data(url)
            if data:
                if not is_filter_mode or any(target.strip() in data['company_name'] for target in target_companies):
                    news_list_data.append(data)
                    print(f"[수집] {data['company_name']} - {data['title']}")
            time.sleep(0.3)

        if debug_save and news_list_data:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(news_list_data, f, ensure_ascii=False, indent=4)
            print(f"\n[성공] {len(news_list_data)}건의 데이터 저장 완료: {output_file}")

        return news_list_data

    except Exception as e:
        print(f"[오류] 목록 수집 중단: {e}")
        return []