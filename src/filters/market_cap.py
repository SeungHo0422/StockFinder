import pandas as pd
from typing import Any, Dict
from .base import BaseStockFilter

class MarketCapFilter(BaseStockFilter):
    def apply(self, df: pd.DataFrame, value: Dict[str, Any]) -> pd.DataFrame:
        min_cap = value.get('min')
        max_cap = value.get('max')
        if min_cap is not None:
            df = df[df['market_cap'] >= min_cap]
        if max_cap is not None:
            df = df[df['market_cap'] <= max_cap]
        return df

    def form_field(self) -> Dict[str, Any]:
        return {
            'name': 'market_cap',
            'label': 'Market Cap',
            'type': 'range',
            'min_placeholder': '최소 시가총액',
            'max_placeholder': '최대 시가총액',
        } 