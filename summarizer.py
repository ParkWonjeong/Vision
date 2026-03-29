import os
import json
from google import genai
from google.genai import types

def summarize_news(articles):
    # This function is used to summarize news into geek news style
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다.")
        
    client = genai.Client(api_key=api_key)
    model_name = "gemini-2.5-flash"
    
    print(f"🧠 {model_name} 모델로 뉴스 분석 및 요약 중...")
    
    system_instruction = """
    당신은 전문 경제 언론의 에디터입니다.
    기사들을 분석하여 지정된 JSON 구조로 완벽히 반환하세요.
    - title_en: 원래 영어 제목
    - title_ko: 한국어 제목 번역
    - link: 기사의 원본 링크
    - summary_ko: 기사 내용을 팩트 위주로 3~4줄 요약한 리스트
    """
    
    prompt = "다음 기사들을 분석해주세요:\n\n"
    for i, article in enumerate(articles):
        prompt += f"[기사 {i+1}]\n제목: {article['title']}\n링크: {article['link']}\n본문:\n{article['content']}\n\n"
        
    response_schema = types.Schema(
        type=types.Type.ARRAY,
        items=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "title_en": types.Schema(type=types.Type.STRING),
                "title_ko": types.Schema(type=types.Type.STRING),
                "link": types.Schema(type=types.Type.STRING),
                "summary_ko": types.Schema(
                    type=types.Type.ARRAY, 
                    items=types.Schema(type=types.Type.STRING)
                ),
            },
            required=["title_en", "title_ko", "link", "summary_ko"],
        ),
    )
    
    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            response_schema=response_schema,
            temperature=0.3, 
        ),
    )
    
    try:
        return json.loads(response.text)
    except Exception as e:
        print(f"❌ 뉴스 요약 파싱 실패: {e}")
        return []

def get_market_study_and_commentary(market_data):
    # This function is used to create a short market commentary + quant/economics study section.
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    
    print(f"🧠 시장 흐름 분석 및 교육 코너 자료 생성 중...")
    
    prompt = f"""
    현재 글로벌 주요 지수와 시장 데이터입니다.
    
    {json.dumps(market_data, ensure_ascii=False, indent=2)}
    
    이 데이터를 바탕으로 두 가지 역할을 수행하여 JSON으로 반환하세요.
    
    1. commentary: 시장 흐름 총평
    - 위 데이터(증시 상승/하락, 환율, 금리 변동)를 보고 어제/오늘 시장이 왜 이런 변동성을 보였는지, 현재 글로벌 경제의 핵심 동력이 무엇인지 '아주 간략하게 3~4줄로' 논리적으로 연결해서 투자자에게 브리핑해주세요. 거짓말(환각)을 하지 말고 일반적인 거시경제 원칙에 비추어 설명하세요.
    
    2. study: 경제/퀀트 교육 코너
    - 매일 다른 새로운 '경제/금융 단어(economic_term)' 1개와 '알고리즘 트레이딩 또는 퀀트 투자 개념(quant_concept)' 1개를 무작위로 선정해서 공부할 수 있도록 제공해주세요.
    - 예시 (단어): 연착륙(Soft Landing), 골디락스, 매파와 비둘기파, 양적완화, 스태그플레이션 등
    - 예시 (퀀트): RSI (Relative Strength Index), 켈리 공식 (Kelly Criterion), 샤프 지수 (Sharpe Ratio), 리스크 패리티, 모멘텀 전략, 페어 트레이딩 등
    - 선정된 단어는 정의와 함께 실전에서 어떻게 쓰이는지 간결하게 설명해야 합니다.
    """
    
    response_schema = types.Schema(
        type=types.Type.OBJECT,
        properties={
            "commentary": types.Schema(
                type=types.Type.ARRAY, 
                items=types.Schema(type=types.Type.STRING), 
                description="시장 상황 분석 문장들"
            ),
            "study": types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "economic_term_name": types.Schema(type=types.Type.STRING),
                    "economic_term_desc": types.Schema(type=types.Type.STRING),
                    "quant_concept_name": types.Schema(type=types.Type.STRING),
                    "quant_concept_desc": types.Schema(type=types.Type.STRING),
                },
                required=["economic_term_name", "economic_term_desc", "quant_concept_name", "quant_concept_desc"]
            )
        },
        required=["commentary", "study"]
    )
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=response_schema,
            temperature=0.7, 
        ),
    )
    
    try:
        data = json.loads(response.text)
        print("✅ 시장 분석 및 스터디 자료 생성 완료.")
        return data
    except Exception as e:
        print(f"❌ 분석 파싱 실패: {e}")
        return {}
