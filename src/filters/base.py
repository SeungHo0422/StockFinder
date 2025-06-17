import pandas as pd
from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseStockFilter(ABC):
    @abstractmethod
    def apply(self, df: pd.DataFrame, value: Any) -> pd.DataFrame:
        """필터 조건을 DataFrame에 적용"""
        pass

    @abstractmethod
    def form_field(self) -> Dict[str, Any]:
        """프론트엔드 폼 생성을 위한 필드 정보 반환 (name, label, type 등)"""
        pass 