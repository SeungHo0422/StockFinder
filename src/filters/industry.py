import pandas as pd
from typing import Any, Dict
from .base import BaseStockFilter

class IndustryFilter(BaseStockFilter):
    def apply(self, df: pd.DataFrame, value: Any) -> pd.DataFrame:
        if value:
            df = df[df['industry'] == value]
        return df

    def form_field(self) -> Dict[str, Any]:
        return {
            'name': 'industry',
            'label': 'Industry',
            'type': 'select',
            'placeholder': '업종 선택',
        } 