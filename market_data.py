import yfinance as yf

def get_market_indices():
    print("📈 실시간 글로벌 시장 지수 수집 중...")
    
    # 트래킹 할 핵심 티커들 (S&P500, 나스닥, 원달러, 비트코인, 미국채 10년물 금리 등)
    tickers = {
        "S&P 500": "^GSPC",
        "나스닥 (NASDAQ)": "^IXIC",
        "원/달러 환율": "KRW=X",
        "비트코인 (BTC)": "BTC-USD",
        "코스피": "^KS11"
    }
    
    indices_data = []
    
    for name, ticker in tickers.items():
        try:
            # period="5d" 로 최근 5일 데이터를 가져옵니다 (전일비 계산용)
            t = yf.Ticker(ticker)
            hist = t.history(period="5d")
            
            if len(hist) >= 2:
                # 마지막 두 개의 종가를 비교 (가장 최근 종가 vs 전 거래일 종가)
                current_price = hist['Close'].iloc[-1]
                prev_price = hist['Close'].iloc[-2]
                
                change = current_price - prev_price
                change_percent = (change / prev_price) * 100
                
                # 시각적으로 구분하기 위해 포맷팅
                if change > 0:
                    status = "up"
                    symbol = "▲"
                elif change < 0:
                    status = "down"
                    symbol = "▼"
                else:
                    status = "flat"
                    symbol = "-"
                
                # 종목마다 표시 단위 형식 맞추기
                if "환율" in name or "S&P" in name or "나스닥" in name:
                    price_str = f"{current_price:,.2f}"
                    change_str = f"{change:,.2f}"
                elif "금리" in name:
                    price_str = f"{current_price:,.3f}%"
                    change_str = f"{change:,.3f}bp" # 금리는 pt 자체가 %이므로 편의상 %나 bp 표시
                else: # 비트코인 등
                    price_str = f"${current_price:,.0f}"
                    change_str = f"${change:,.0f}"
                
                indices_data.append({
                    "name": name,
                    "price": price_str,
                    "change": change_str,
                    "change_percent": f"{change_percent:+.2f}%",
                    "status": status,
                    "symbol": symbol
                })
        except Exception as e:
            print(f"⚠️ {name} ({ticker}) 수집 오류: {e}")
            
    print("✅ 시장 데이터 수집 완료.")
    return indices_data
