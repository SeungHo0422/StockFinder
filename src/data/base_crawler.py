from abc import ABC, abstractmethod
import pandas as pd
from typing import List

class BaseStockCrawler(ABC):
    @abstractmethod
    def get_us_stocks(self) -> pd.DataFrame:
        """미국 주식 목록을 DataFrame으로 반환"""
        pass

    @abstractmethod
    def get_stock_recent_data(self, symbol: str, n_days: int = 5) -> pd.DataFrame:
        """특정 심볼의 최근 n일간 시세를 DataFrame으로 반환"""
        pass 