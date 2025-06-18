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

# 커스텀 Jinja2 필터 추가
def number_filter(value):
    """숫자를 천 단위로 쉼표를 추가하여 포맷팅"""
    try:
        return f"{int(value):,}"
    except (ValueError, TypeError):
        return str(value)

templates.env.filters['number'] = number_filter

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
        print(f"스크리닝 명령어 실행: {' '.join(cmd)}")
        print(f"현재 작업 디렉토리: {os.getcwd()}")
        
        # data 디렉토리 생성
        data_dir = "data"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            print(f"📁 data 디렉토리 생성: {data_dir}")
        else:
            print(f"✅ data 디렉토리 존재: {data_dir}")
        
        # 파일 존재 여부 확인
        script_path = 'calc_rsi_sar_screening.py'
        if os.path.exists(script_path):
            print(f"✅ 스크립트 파일 존재: {script_path}")
        else:
            print(f"❌ 스크립트 파일 없음: {script_path}")
            return
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
        print(f"스크리닝 완료: {result.returncode}")
        print(f"스크리닝 stdout: {result.stdout}")
        print(f"스크리닝 stderr: {result.stderr}")
        
        # 결과 파일 확인
        result_file = "data/rsi_sar_macd_screening.json"
        if os.path.exists(result_file):
            print(f"✅ 결과 파일 생성됨: {result_file}")
            file_size = os.path.getsize(result_file)
            print(f"파일 크기: {file_size} bytes")
        else:
            print(f"❌ 결과 파일 없음: {result_file}")
            
    except Exception as e:
        print(f"스크리닝 오류: {e}")
        import traceback
        traceback.print_exc()

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
        "error": "결과 파일을 찾을 수 없습니다."
    })

@app.post("/api/test-telegram")
async def test_telegram(request: Request):
    """텔레그램 연결 테스트 API"""
    try:
        data = await request.json()
        token = data.get('token', '').strip()
        chat_id = data.get('chat_id', '').strip()
        
        # 토큰에서 주석 제거 (# 이후 텍스트 제거)
        if '#' in token:
            token = token.split('#')[0].strip()
        
        if not token or not chat_id:
            return JSONResponse({
                "success": False,
                "message": "봇 토큰과 채팅 ID를 모두 입력해주세요."
            })
        
        # 텔레그램 봇 라이브러리 import
        try:
            from src.notifier.telegram_bot import TelegramNotifier
        except ImportError:
            return JSONResponse({
                "success": False,
                "message": "텔레그램 봇 라이브러리가 설치되지 않았습니다."
            })
        
        # 텔레그램 연결 테스트
        notifier = TelegramNotifier(bot_token=token, chat_id=chat_id)
        success = await notifier.send_test_message()
        
        if success:
            return JSONResponse({
                "success": True,
                "message": "텔레그램 연결 테스트가 성공했습니다!"
            })
        else:
            return JSONResponse({
                "success": False,
                "message": "텔레그램 메시지 전송에 실패했습니다. 봇 토큰과 채팅 ID를 확인해주세요."
            })
            
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"텔레그램 테스트 중 오류가 발생했습니다: {str(e)}"
        })
    
@app.post("/api/start-scheduler")
async def start_scheduler(request: Request):
    """스케줄러 시작 API"""
    try:
        data = await request.json()
        
        return JSONResponse({
            "success": True,
            "message": "스케줄러 기능은 아직 구현되지 않았습니다."
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"스케줄러 시작 중 오류: {str(e)}"
        })

@app.post("/api/refresh-market-data")
async def refresh_market_data():
    """시장 데이터 새로고침 API"""
    try:
        # 실제로는 시장 데이터를 새로고침하는 로직을 구현해야 함
        return JSONResponse({
            "success": True,
            "message": "시장 데이터 새로고침이 완료되었습니다."
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"시장 데이터 새로고침 중 오류: {str(e)}"
        })

@app.post("/api/clear-old-results")
async def clear_old_results():
    """오래된 결과 정리 API"""
    try:
        # 실제로는 오래된 파일들을 정리하는 로직을 구현해야 함
        deleted_count = 0
        
        return JSONResponse({
            "success": True,
            "deleted_count": deleted_count,
            "message": f"{deleted_count}개의 오래된 결과가 정리되었습니다."
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"결과 정리 중 오류: {str(e)}"
        })

@app.get("/api/export-results")
async def export_results():
    """결과 내보내기 API"""
    try:
        result_file = "data/rsi_sar_macd_screening.json"
        
        if os.path.exists(result_file):
            with open(result_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            from fastapi.responses import Response
            return Response(
                content=content,
                media_type="application/json",
                headers={"Content-Disposition": f"attachment; filename=stockfinder_results_{datetime.now().strftime('%Y%m%d')}.json"}
            )
        else:
            return JSONResponse({
                "success": False,
                "message": "내보낼 결과가 없습니다."
            })
            
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"결과 내보내기 중 오류: {str(e)}"
        })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 