from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from src.data.collector import get_us_stocks
from src.filters import FILTERS
import pandas as pd

app = FastAPI()
templates = Jinja2Templates(directory="src/web/templates")

@app.get("/stocks", response_class=HTMLResponse)
def stocks(request: Request):
    df: pd.DataFrame = get_us_stocks()
    query = request.query_params
    filter_fields = [f.form_field() for f in FILTERS]

    # 필터 적용
    for f in FILTERS:
        field = f.form_field()
        name = field['name']
        if field['type'] == 'range':
            min_val = query.get(f"{name}_min")
            max_val = query.get(f"{name}_max")
            value = {}
            if min_val:
                try:
                    value['min'] = float(min_val)
                except ValueError:
                    pass
            if max_val:
                try:
                    value['max'] = float(max_val)
                except ValueError:
                    pass
            if value:
                df = f.apply(df, value)
        elif field['type'] == 'select':
            val = query.get(name)
            if val:
                df = f.apply(df, val)

    # 업종(Industry) 목록 추출 (select 옵션용)
    industry_options = []
    if 'industry' in df.columns:
        industry_options = sorted(df['industry'].dropna().unique().tolist())
    
    stocks = df.head(20).to_dict(orient="records")
    columns = df.columns.tolist()
    return templates.TemplateResponse(
        "stocks.html",
        {
            "request": request,
            "stocks": stocks,
            "columns": columns,
            "filter_fields": filter_fields,
            "industry_options": industry_options,
        }
    ) 