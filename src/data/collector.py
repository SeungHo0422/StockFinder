from .base_crawler import BaseStockCrawler
from .investing_crawler import InvestingComCrawler

# 기본 크롤러 인스턴스 (확장성 고려)
crawler: BaseStockCrawler = InvestingComCrawler()

def get_us_stocks():
    return crawler.get_us_stocks()

def get_stock_recent_data(symbol: str, n_days: int = 5):
    return crawler.get_stock_recent_data(symbol, n_days)

if __name__ == "__main__":
    stocks = get_us_stocks()
    print(f"미국 상장 주식 수: {len(stocks)}")
    print(stocks.head())
    # 예시: 애플 최근 5일 데이터
    apple = get_stock_recent_data('AAPL', 5)
    print(apple) 