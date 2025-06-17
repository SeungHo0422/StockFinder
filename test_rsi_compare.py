import pandas as pd
from pykrx import stock
from datetime import datetime, timedelta
from src.data.indicators import calculate_rsi, calculate_rsi_wilder, get_stock_rsi

def test_samsung_rsi():
    """삼성전자 RSI 테스트 - Wilder vs EMA 비교"""
    ticker = "005930"  # 삼성전자
    print(f"=== 삼성전자({ticker}) RSI 분석 ===")
    
    # 충분한 과거 데이터 가져오기 (300일)
    end = datetime.today()
    start = end - timedelta(days=400)  
    
    df = stock.get_market_ohlcv_by_date(
        start.strftime("%Y%m%d"),
        end.strftime("%Y%m%d"),
        ticker
    )
    
    print(f"데이터 기간: {df.index[0]} ~ {df.index[-1]}")
    print(f"총 {len(df)}일치 데이터")
    print()
    
    # 두 방식으로 RSI 계산
    rsi_ema = calculate_rsi(df['종가'], period=14)
    rsi_wilder = calculate_rsi_wilder(df['종가'], period=14)
    
    # 최근 10일 비교
    print("=== RSI 비교 (최근 10일) ===")
    print("날짜\t\t\t종가\t\tEMA RSI\t\tWilder RSI")
    print("-" * 65)
    
    recent_data = df.tail(300)
    for idx, row in recent_data.iterrows():
        ema_val = rsi_ema.loc[idx] if pd.notna(rsi_ema.loc[idx]) else "N/A"
        wilder_val = rsi_wilder.loc[idx] if pd.notna(rsi_wilder.loc[idx]) else "N/A"
        close_price = f"{row['종가']:,}"
        
        ema_str = f"{ema_val:.2f}" if isinstance(ema_val, float) else str(ema_val)
        wilder_str = f"{wilder_val:.2f}" if isinstance(wilder_val, float) else str(wilder_val)
            
        print(f"{idx.strftime('%Y-%m-%d')}\t{close_price:>8}\t{ema_str:>8}\t{wilder_str:>10}")
    
    # 최신 RSI 값들
    latest_ema = rsi_ema.iloc[-1]
    latest_wilder = rsi_wilder.iloc[-1]
    
    print(f"\n=== 최신 RSI 값 ===")
    print(f"EMA 방식: {latest_ema:.2f}")
    print(f"Wilder 방식: {latest_wilder:.2f}")
    print(f"get_stock_rsi(Wilder): {get_stock_rsi(ticker, use_wilder=True):.2f}")
    print(f"get_stock_rsi(EMA): {get_stock_rsi(ticker, use_wilder=False):.2f}")
    
    # 계산 과정 비교 (최근 20일 중 마지막 5일)
    print(f"\n=== Wilder RSI 계산 상세 (최근 5일) ===")
    recent_20 = df.tail(20).copy()
    
    # 수동으로 Wilder 방식 계산해보기
    delta = recent_20['종가'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    print("날짜\t\t종가\t변화\t상승\t하락\tRSI")
    print("-" * 60)
    
    for idx, row in recent_20.tail(5).iterrows():
        rsi_val = rsi_wilder.loc[idx]
        delta_val = delta.loc[idx] if pd.notna(delta.loc[idx]) else 0
        gain_val = gain.loc[idx]
        loss_val = loss.loc[idx]
        
        print(f"{idx.strftime('%m-%d')}\t{row['종가']:,}\t{delta_val:+.0f}\t{gain_val:.0f}\t{loss_val:.0f}\t{rsi_val:.2f}")

if __name__ == "__main__":
    test_samsung_rsi() 