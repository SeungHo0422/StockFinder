import pandas as pd
from typing import Any, Dict
from .base import BaseStockFilter

class PERatioFilter(BaseStockFilter):
    def apply(self, df: pd.DataFrame, value: Dict[str, Any]) -> pd.DataFrame:
        min_pe = value.get('min')
        max_pe = value.get('max')
        if min_pe is not None:
            df = df[df['pe_ratio'] >= min_pe]
        if max_pe is not None:
            df = df[df['pe_ratio'] <= max_pe]
        return df

    def form_field(self) -> Dict[str, Any]:
        return {
            'name': 'pe_ratio',
            'label': 'P/E Ratio',
            'type': 'range',
            'min_placeholder': '최소 PER',
            'max_placeholder': '최대 PER',
        } 