import os
import smtplib
from email.message import EmailMessage
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import pytz

def create_html(articles, indices, commentary, study):
    print("🎨 HTML 이메일 템플릿 렌더링 중...")
    
    template_dir = 'templates' if os.path.exists('templates') else '.'
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template('newsletter.html')
    
    korea_tz = pytz.timezone('Asia/Seoul')
    today = datetime.now(korea_tz).strftime('%Y년 %m월 %d일')
    
    html_content = template.render(
        today_date=today,
        articles=articles,
        indices=indices,
        commentary=commentary,
        study=study
    )
    return html_content, today

def send_email(html_content, today_date, dry_run=False):
    if dry_run:
        print("💾 Dry run 모드: 이메일을 보내는 대신 HTML 파일로 저장합니다.")
        with open('preview.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        print("✅ preview.html 로 저장완료.")
        return

    sender_email = os.getenv("EMAIL_ADDRESS")
    sender_password = os.getenv("EMAIL_PASSWORD")
    receiver_email = os.getenv("RECEIVER_EMAIL", sender_email)
    
    if not sender_email or not sender_password:
        raise ValueError("EMAIL_ADDRESS 또는 EMAIL_PASSWORD 환경 변수가 누락되었습니다.")
        
    print(f"✉️ 이메일 발송 준비 중... (Target: {receiver_email})")
    
    msg = EmailMessage()
    msg['Subject'] = f"[바건정 Vision] {today_date} 글로벌 시장 & 퀀트 브리핑"
    msg['From'] = f"Vision Newsletter <{sender_email}>"
    msg['To'] = receiver_email
    
    msg.set_content("이 메일은 HTML 형식을 지원하는 클라이언트에서만 확인할 수 있습니다.")
    msg.add_alternative(html_content, subtype='html')
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)
        print("✅ 성공적으로 뉴스레터를 발송했습니다!")
    except Exception as e:
        print(f"❌ 이메일 발송 실패: {e}")
