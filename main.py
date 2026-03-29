import os
import argparse
from dotenv import load_dotenv
from crawler import get_latest_news
from summarizer import summarize_news, get_market_study_and_commentary
from market_data import get_market_indices
from mailer import create_html, send_email

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--preview", action="store_true", help="메일을 보내지 않고 로컬에 preview.html 로 저장")
    args = parser.parse_args()

    print("="*50)
    print("🌐 Vision 경제/퀀트 브리핑 생성 시작")
    print("="*50)
    
    load_dotenv(override=True)
    
    # 1. 시장 데이터 가져오기 (실시간 지수 시세)
    indices_data = get_market_indices()
    
    # 2. 시장 분석 코멘터리 및 스터디 (경제/퀀트) 자료 생성 (Gemini)
    study_n_commentary = get_market_study_and_commentary(indices_data)
    commentary = study_n_commentary.get("commentary", [])
    study = study_n_commentary.get("study", {})
    
    # 3. 최신 경제 뉴스 크롤링
    articles = get_latest_news(limit=4)
    if not articles:
        print("❌ 수집된 기사가 없습니다. 프로그램을 종료합니다.")
        return
        
    # 4. 기사 AI 구조화 요약
    summarized_data = summarize_news(articles)
    if not summarized_data:
        print("❌ AI 뉴스 요약 파싱에 실패했습니다.")
        return
        
    # 5. 모든 데이터를 넣고 HTML 프리미엄 템플릿 생성
    html_content, today_date = create_html(
        articles=summarized_data,
        indices=indices_data,
        commentary=commentary,
        study=study
    )
    
    # 6. 발송 (혹은 로컬 저장)
    send_email(html_content, today_date, dry_run=args.preview)
    
    print("="*50)
    print("✨ 모든 자동화 프로세스가 완료되었습니다 ✨")
    print("="*50)

if __name__ == "__main__":
    main()