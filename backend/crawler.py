import requests
import time
import random
from bs4 import BeautifulSoup


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
}

# --- [파트 1] 사용자님이 만드신 고성능 상세 수집기 (그대로 사용) ---
def get_news_details(url):

    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # 1. 제목
        title = soup.select_one('h2#title_area span').get_text(strip=True) if soup.select_one('h2#title_area span') else "제목 없음"

        # 2. 시간
        time_el = soup.select_one('.media_end_head_info_datestamp_time._ARTICLE_DATE_TIME')
        published_at = time_el['data-date-time'] if time_el and time_el.has_attr('data-date-time') else None

        # 3. 신문사
        publisher = soup.select_one('.media_end_head_top_logo img')['title'] if soup.select_one('.media_end_head_top_logo img') else "언론사 미상"

        # 4. 이미지 (대표 이미지 1개만 DB에 넣기 위해 첫 번째 것만 가져옴)
        image_url = None
        img_tag = soup.select_one('#newsct_article img')
        if img_tag:
            image_url = img_tag.get('data-src') or img_tag.get('src')

        # 5. 본문 내용 (노이즈 제거 로직 유지)
        content_area = soup.select_one('#newsct_article')
        if content_area:
            for extra in content_area.select('.img_desc, .article_caption, em, script, style'):
                extra.decompose()
            content = content_area.get_text(separator=' ', strip=True)
        else:
            content = "내용 없음"

        return {
            "title": title,
            "published_at": published_at,
            "publisher": publisher,
            "content": content,
            "image_url": image_url,
            "url": url
        }

    except Exception as e:
        print(f"❌ 오류 발생 ({url}): {e}")
        return None


# --- [파트 2] 검색해서 URL을 물어오는 탐색기 (새로 추가됨) ---
def crawl_breaking_news(limit=20, db_check_session=None):
    """
    네이버 속보 리스트를 가져옵니다.
    db_check_session이 있으면 중복 기사 확인 시 수집을 멈춥니다.
    """
    # 1. 함수 안에서 crud 함수 가져오기 (순환 참조 방지)
    from crud import is_url_exists 

    print(f"📡 속보 확인 중... (최대 {limit}개 탐색)")
    
    # 2. 속보 페이지 요청
    base_url = "https://news.naver.com/main/list.naver?mode=LSD&mid=sec&sid1=001"
    response = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    articles_ul = soup.select('.list_body ul.type06_headline li, .list_body ul.type06 li')
    
    results = []
    collected_urls = set()
    count = 0

    for li in articles_ul:
        if count >= limit:
            break
            
        a_tags = li.select('dl dt a')
        for a in a_tags:
            url = a['href']
            
            # 중복 URL이거나 네이버 뉴스가 아니면 패스
            if url in collected_urls or "news.naver.com" not in url:
                continue
            
            # 🔥 [핵심] DB에 이미 있는 기사인지 확인
            if db_check_session and is_url_exists(db_check_session, url):
                print(f"  🛑 [중단] 이미 수집한 기사를 만났습니다! ({url})")
                print(f"     이 이후로는 이전 뉴스이므로 수집을 멈춥니다.")
                return results # 여기서 함수 종료

            collected_urls.add(url)
            
            # 상세 수집
            print(f"  [{count+1}] 새 뉴스 수집: {url}")
            article = get_news_details(url) # 위에 정의된 상세 수집 함수 호출
            
            if article:
                results.append(article)
                count += 1
                if count >= limit:
                    break
            
            # 차단 방지용 딜레이
            time.sleep(random.uniform(0.3, 0.8))

    return results