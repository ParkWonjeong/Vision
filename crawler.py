import feedparser
import requests
from bs4 import BeautifulSoup
import re

# CNBC Business News RSS
RSS_URL = "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10001147"

def clean_html(raw_html):
    soup = BeautifulSoup(raw_html, "html.parser")
    text = soup.get_text()
    # 연속된 공백이나 줄바꿈을 하나로 치환
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def get_latest_news(limit=4):
    print(f"📡 {RSS_URL} 에서 뉴스 크롤링 중...")
    feed = feedparser.parse(RSS_URL)
    
    articles = []
    
    for entry in feed.entries[:limit]:
        title = entry.title
        link = entry.link
        
        # summary가 HTML 태그를 포함하기도 합니다.
        summary = entry.get('summary', '')
        summary_text = clean_html(summary)
        
        # 더 나은 요약을 위해 실제 기사 본문 페이지 스크래핑을 시도합니다.
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            response = requests.get(link, headers=headers, timeout=5)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                # 보통 본문은 <p> 태그에 담겨 있습니다.
                paragraphs = soup.find_all('p')
                # 상위 10개 문단 정도만 합쳐도 AI가 요약하기에 충분한 맥락이 제공됩니다.
                body_text = " ".join([p.get_text() for p in paragraphs[:10]])
                if len(body_text) > 200:
                    summary_text = clean_html(body_text)
        except Exception as e:
            print(f"⚠️ 원문 스크래핑 실패. 요약본만 사용합니다 ({link}): {e}")
            pass
            
        articles.append({
            'title': title,
            'link': link,
            'content': summary_text
        })
        
    print(f"✅ {len(articles)}개의 뉴스 수집 완료.")
    return articles
