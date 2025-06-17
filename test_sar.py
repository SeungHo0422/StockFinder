import pandas as pd
from pykrx import stock
from datetime import datetime, timedelta
from src.data.indicators import calculate_parabolic_sar, calculate_sar_signal, get_stock_rsi, get_stock_sar_signal

def test_samsung_sar():
    """삼성전자 Parabolic SAR 테스트"""
    ticker = "005930"  # 삼성전자
    print(f"=== 삼성전자({ticker}) Parabolic SAR 분석 ===")
    
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
    
    # SAR 계산
    sar = calculate_parabolic_sar(df['고가'], df['저가'], df['종가'])
    signals = calculate_sar_signal(df['고가'], df['저가'], df['종가'], sar)
    
    # 최근 15일 상세 분석
    print("=== 최근 15일 SAR 분석 (시가 기준) ===")
    print("날짜\t\t고가\t저가\t시가\tSAR\t\t신호\t추세")
    print("-" * 80)
    
    recent_data = df.tail(15)
    recent_sar = sar.tail(15)
    recent_signals = signals.tail(15)
    
    for i, (idx, row) in enumerate(recent_data.iterrows()):
        sar_val = recent_sar.iloc[i]
        signal_val = recent_signals.iloc[i]
        
        # 추세 판단 (시가 기준)
        if row['시가'] > sar_val:
            trend = "상승"
        else:
            trend = "하락"
        
        # 신호 텍스트
        if signal_val == 1:
            signal_text = "매수"
        elif signal_val == -1:
            signal_text = "매도"
        else:
            signal_text = "-"
        
        print(f"{idx.strftime('%m-%d')}\t{row['고가']:,}\t{row['저가']:,}\t{row['시가']:,}\t{sar_val:.0f}\t\t{signal_text}\t{trend}")
    
    # 현재 상태
    current_sar = sar.iloc[-1]
    current_open = df['시가'].iloc[-1]  # 종가 대신 시가 사용
    current_signal = signals.iloc[-1]
    
    print(f"\n=== 현재 상태 (시가 기준) ===")
    print(f"현재 시가: {current_open:,}원")
    print(f"현재 SAR: {current_sar:.0f}원")
    
    if current_open > current_sar:
        print(f"현재 추세: 상승 (시가가 SAR 위에 위치)")
    else:
        print(f"현재 추세: 하락 (시가가 SAR 아래에 위치)")
    
    # 최근 신호 확인
    recent_signals_non_zero = recent_signals[recent_signals != 0]
    if not recent_signals_non_zero.empty:
        last_signal_date = recent_signals_non_zero.index[-1]
        last_signal_value = recent_signals_non_zero.iloc[-1]
        if last_signal_value == 1:
            print(f"최근 신호: {last_signal_date.strftime('%m-%d')} 매수 신호")
        else:
            print(f"최근 신호: {last_signal_date.strftime('%m-%d')} 매도 신호")
    else:
        print(f"최근 신호: 없음")
    
    # RSI와 함께 분석
    current_rsi = get_stock_rsi(ticker)
    print(f"\n=== 종합 분석 (시가 기준) ===")
    print(f"RSI: {current_rsi:.2f}")
    print(f"SAR 추세: {'상승' if current_open > current_sar else '하락'}")
    
    # 매수 타이밍 분석 (시가 기준)
    if current_rsi < 30 and current_open > current_sar:
        print("🔥 강력한 매수 신호! (과매도 + SAR 상승추세)")
    elif current_rsi < 30:
        print("⚠️  과매도 상태, SAR 반전 대기")
    elif current_open > current_sar and 30 <= current_rsi <= 50:
        print("✅ 좋은 매수 구간 (정상 RSI + SAR 상승추세)")
    else:
        print("📊 관망 권장")
    
    # get_stock_sar_signal 함수 테스트
    print(f"\n=== SAR 신호 함수 테스트 ===")
    sar_result = get_stock_sar_signal(ticker)
    print(f"SAR 분석 결과: {sar_result}")

if __name__ == "__main__":
    test_samsung_sar() 