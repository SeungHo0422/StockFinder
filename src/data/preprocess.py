import pandas as pd
import re

def preprocess_stock_table(df: pd.DataFrame) -> pd.DataFrame:
    # 1. 컬럼명 정규화 (공백, 특수문자 제거, 소문자화)
    df = df.rename(columns=lambda x: re.sub(r'[^\w]+', '_', x.strip().lower()))

    # 2. 주요 필드만 남기기 (예시: symbol, name, last, change, change_percent, volume 등)
    keep_cols = [
        'symbol', 'name', 'last', 'change', 'change_', 'change_percent', 'volume', 'market_cap', 'pe_ratio', 'sector', 'industry'
    ]
    # 실제 존재하는 컬럼만 남기기
    keep_cols = [col for col in keep_cols if col in df.columns]
    df = df[keep_cols]

    # 3. 숫자형 컬럼 변환 (쉼표, % 등 제거)
    for col in ['last', 'change', 'change_', 'change_percent', 'volume', 'market_cap', 'pe_ratio']:
        if col in df.columns:
            df[col] = (
                df[col].astype(str)
                .str.replace(',', '', regex=False)
                .str.replace('%', '', regex=False)
                .str.replace('−', '-', regex=False)  # 마이너스 기호 통일
            )
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # 4. 결측치/이상치 처리 (필요시)
    df = df.dropna(subset=['name'])
    df = df.reset_index(drop=True)
    return df 