from fastapi import FastAPI, Request, Form, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import json
import os
from datetime import datetime
import subprocess
import sys
from typing import Optional

app = FastAPI(title="StockFinder", description="한국 주식 스크리닝 및 분석 도구")
templates = Jinja2Templates(directory="src/web/templates")

# 정적 파일 서빙 (CSS, JS, 이미지 등)
app.mount("/static", StaticFiles(directory="src/web/static"), name="static")

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    """메인 홈페이지"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/screening", response_class=HTMLResponse)
def screening_page(request: Request):
    """스크리닝 페이지"""
    return templates.TemplateResponse("screening.html", {"request": request})

@app.get("/results", response_class=HTMLResponse)
def results_page(request: Request):
    """결과 페이지"""
    # 최신 스크리닝 결과 파일 확인
    result_file = "data/rsi_sar_macd_screening.json"
    results = None
    if os.path.exists(result_file):
        try:
            with open(result_file, 'r', encoding='utf-8') as f:
                results = json.load(f)
        except:
            pass
    
    return templates.TemplateResponse("results.html", {
        "request": request,
        "results": results
    })

@app.get("/settings", response_class=HTMLResponse)
def settings_page(request: Request):
    """설정 페이지"""
    return templates.TemplateResponse("settings.html", {"request": request})

@app.post("/api/run-screening")
async def run_screening(
    background_tasks: BackgroundTasks,
    rsi_threshold: float = Form(30.0),
    market: str = Form("ALL"),
    send_telegram: bool = Form(False)
):
    """스크리닝 실행 API"""
    try:
        # 스크리닝 명령어 구성
        cmd = [
            sys.executable, 
            'calc_rsi_sar_screening.py',
            '--rsi-max', str(rsi_threshold),
            '--market', market,
            '--workers', '4'
        ]
        
        if send_telegram:
            cmd.append('--telegram')
        
        # 백그라운드에서 실행
        background_tasks.add_task(run_screening_task, cmd)
        
        return JSONResponse({
            "success": True,
            "message": "스크리닝이 시작되었습니다. 잠시 후 결과를 확인해주세요."
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"스크리닝 실행 중 오류가 발생했습니다: {str(e)}"
        })

def run_screening_task(cmd):
    """백그라운드 스크리닝 실행"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(f"스크리닝 완료: {result.returncode}")
    except Exception as e:
        print(f"스크리닝 오류: {e}")

@app.get("/api/screening-status")
async def get_screening_status():
    """스크리닝 상태 확인 API"""
    result_file = "data/rsi_sar_macd_screening.json"
    
    if os.path.exists(result_file):
        try:
            with open(result_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return JSONResponse({
                "has_results": True,
                "last_update": data.get("analysis_date", ""),
                "target_market": data.get("target_market", "ALL"),
                "rsi_threshold": data.get("rsi_threshold", 30.0),
                "total_stocks": data.get("total_stocks", 0),
                "golden_cross_count": data.get("golden_cross_count", 0),
                "sar_buy_count": data.get("sar_buy_count", 0)
            })
        except:
            pass
    
    return JSONResponse({
        "has_results": False,
        "message": "스크리닝 결과가 없습니다."
    })

@app.get("/api/market-stats")
async def get_market_stats():
    """시장별 통계 API"""
    try:
        from pykrx import stock
        
        markets = {
            "KOSPI": "코스피",
            "KOSDAQ": "코스닥", 
            "KONEX": "코넥스",
            "ALL": "전체"
        }
        
        stats = {}
        for market_code, market_name in markets.items():
            tickers = stock.get_market_ticker_list(market=market_code)
            stats[market_code] = {
                "name": market_name,
                "count": len(tickers)
            }
        
        return JSONResponse(stats)
        
    except Exception as e:
        return JSONResponse({
            "error": str(e)
        })

@app.get("/api/screening-results")
async def get_screening_results():
    """스크리닝 결과 API"""
    result_file = "data/rsi_sar_macd_screening.json"
    
    if os.path.exists(result_file):
        try:
            with open(result_file, 'r', encoding='utf-8') as f:
                results = json.load(f)
            
            return JSONResponse({
                "success": True,
                "results": results
            })
        except Exception as e:
            return JSONResponse({
                "success": False,
                "error": str(e)
            })
    
    return JSONResponse({
        "success": False,
        "message": "스크리닝 결과가 없습니다."
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 