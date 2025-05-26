import requests
import pandas as pd
from bs4 import BeautifulSoup
from .base_crawler import BaseStockCrawler
from .preprocess import preprocess_stock_table
from io import StringIO  # StringIO를 import하여 사용


class InvestingComCrawler(BaseStockCrawler):
    BASE_URL = "https://www.investing.com/stock-screener/"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    def get_us_stocks(self) -> pd.DataFrame:
        """Investing.com의 미국 주식 표 데이터를 DataFrame으로 반환"""
        url = self.BASE_URL
        response = requests.get(url, headers=self.HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table")
        if not table:
            raise ValueError("표를 찾을 수 없습니다.")
        # pd.read_html에 literal string을 넘기지 않고 StringIO로 감싸서 전달
        df = pd.read_html(StringIO(str(table)))[0]
        df = preprocess_stock_table(df)
        return df

    def get_stock_recent_data(self, symbol: str, n_days: int = 5) -> pd.DataFrame:
        # TODO: 개별 종목의 최근 시세 데이터 크롤링 구현
        raise NotImplementedError 
    
if __name__ == "__main__":
    crawler = InvestingComCrawler()
    df = crawler.get_us_stocks()
    print(df)