import pandas as pd
from pykrx import stock
from datetime import datetime, timedelta
from src.data.indicators import calculate_macd, detect_macd_golden_cross, get_stock_macd_signal

def test_samsung_macd():
    """삼성전자 MACD 테스트"""
    ticker = "005930"  # 삼성전자
    print(f"=== 삼성전자({ticker}) MACD 분석 ===")
    
    # 100일 데이터 가져오기
    end = datetime.today()
    start = end - timedelta(days=120)
    
    df = stock.get_market_ohlcv_by_date(
        start.strftime("%Y%m%d"),
        end.strftime("%Y%m%d"),
        ticker
    )
    
    print(f"데이터 기간: {df.index[0]} ~ {df.index[-1]}")
    print(f"총 {len(df)}일치 데이터")
    print()
    
    # MACD 계산
    macd_data = calculate_macd(df['종가'])
    golden_cross_signals = detect_macd_golden_cross(macd_data["macd"], macd_data["signal"])
    
    # 최근 15일 상세 분석
    print("=== 최근 15일 MACD 분석 ===")
    print("날짜\t\t종가\t\tMACD\t\tSignal\t\tHist\t\t골든크로스")
    print("-" * 85)
    
    recent_data = df.tail(15)
    recent_macd = macd_data["macd"].tail(15)
    recent_signal = macd_data["signal"].tail(15)
    recent_histogram = macd_data["histogram"].tail(15)
    recent_golden = golden_cross_signals.tail(15)
    
    for i, (idx, row) in enumerate(recent_data.iterrows()):
        macd_val = recent_macd.iloc[i]
        signal_val = recent_signal.iloc[i]
        hist_val = recent_histogram.iloc[i]
        golden_val = recent_golden.iloc[i]
        
        golden_text = "🟡 골든크로스" if golden_val == 1 else "-"
        
        print(f"{idx.strftime('%m-%d')}\t{row['종가']:,}\t\t{macd_val:.2f}\t\t{signal_val:.2f}\t\t{hist_val:.2f}\t\t{golden_text}")
    
    # 현재 상태
    current_macd = macd_data["macd"].iloc[-1]
    current_signal = macd_data["signal"].iloc[-1]
    current_histogram = macd_data["histogram"].iloc[-1]
    
    print(f"\n=== 현재 MACD 상태 ===")
    print(f"MACD Line: {current_macd:.4f}")
    print(f"Signal Line: {current_signal:.4f}")
    print(f"Histogram: {current_histogram:.4f}")
    
    if current_macd > current_signal:
        print(f"현재 상태: 상승 (MACD가 Signal 위에 위치)")
    else:
        print(f"현재 상태: 하락 (MACD가 Signal 아래에 위치)")
    
    # 최근 골든크로스 확인
    recent_golden_crosses = golden_cross_signals[golden_cross_signals == 1]
    if not recent_golden_crosses.empty:
        last_golden_date = recent_golden_crosses.index[-1]
        print(f"최근 골든크로스: {last_golden_date.strftime('%Y-%m-%d')}")
    else:
        print(f"최근 골든크로스: 없음")
    
    # 최근 5일 내 골든크로스 여부
    recent_5days_golden = any(golden_cross_signals.tail(5) == 1)
    if recent_5days_golden:
        print(f"📈 최근 5일 내 골든크로스 발생!")
    else:
        print(f"📊 최근 5일 내 골든크로스 없음")
    
    # MACD 추세 분석
    print(f"\n=== MACD 추세 분석 ===")
    
    # 히스토그램 추세
    recent_hist = macd_data["histogram"].tail(3)
    if all(recent_hist.diff().dropna() > 0):
        hist_trend = "상승"
    elif all(recent_hist.diff().dropna() < 0):
        hist_trend = "하락"
    else:
        hist_trend = "횡보"
    
    print(f"히스토그램 추세: {hist_trend}")
    print(f"MACD 위치: {'양수' if current_macd > 0 else '음수'}")
    print(f"Signal 위치: {'양수' if current_signal > 0 else '음수'}")
    
    # get_stock_macd_signal 함수 테스트
    print(f"\n=== MACD 신호 함수 테스트 ===")
    macd_result = get_stock_macd_signal(ticker)
    print(f"MACD 분석 결과: {macd_result}")

if __name__ == "__main__":
    test_samsung_macd() 