import investpy
import pandas as pd
from datetime import datetime, timedelta

def get_us_stocks():
    stocks = investpy.stocks.get_stocks(country='united states')
    return stocks

def get_stock_recent_data(symbol: str, n_days: int = 5):
    end_date = datetime.today()
    start_date = end_date - timedelta(days=n_days)
    try:
        df = investpy.stocks.get_stock_historical_data(
            stock=symbol,
            country='united states',
            from_date=start_date.strftime('%d/%m/%Y'),
            to_date=end_date.strftime('%d/%m/%Y')
        )
        return df
    except Exception as e:
        print(f"{symbol} 데이터 수집 실패: {e}")
        return None

if __name__ == "__main__":
    stocks = get_us_stocks()
    print(f"미국 상장 주식 수: {len(stocks)}")
    print(stocks.head())
    # 예시: 애플 최근 5일 데이터
    apple = get_stock_recent_data('AAPL', 5)
    print(apple) 