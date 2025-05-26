import time
import schedule
from src.data.collector import get_stock_recent_data
from src.config.settings import settings

# 모니터링할 주요 종목 리스트 (예시)
MONITOR_SYMBOLS = ["AAPL", "MSFT", "TSLA"]


def monitor_stocks():
    print("\n[실시간 종목 모니터링]")
    for symbol in MONITOR_SYMBOLS:
        df = get_stock_recent_data(symbol, 1)
        if df is not None and not df.empty:
            latest = df.iloc[-1]
            print(f"{symbol} | 날짜: {latest.name.date()} | 종가: {latest['Close']} | 거래량: {latest['Volume']}")
        else:
            print(f"{symbol} 데이터 없음")


def run_monitor():
    schedule.every(settings.MONITOR_INTERVAL_MINUTES).minutes.do(monitor_stocks)
    print(f"{settings.MONITOR_INTERVAL_MINUTES}분마다 실시간 종목 모니터링을 시작합니다...")
    monitor_stocks()  # 최초 1회 실행
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    run_monitor() 