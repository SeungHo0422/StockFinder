import json
import time
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm
from pykrx import stock
from src.data.indicators import get_stock_rsi, get_stock_sar_signal, get_stock_macd_signal
import datetime

# 텔레그램 알림 기능 추가
try:
    from src.notifier.telegram_bot import send_screening_results_sync
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    print("⚠️  텔레그램 알림 기능을 사용하려면 python-telegram-bot을 설치하세요.")

# 시장별 종목 리스트 캐시
_market_cache = {}

def analyze_rsi_only(ticker):
    """1차 필터링: RSI만 계산"""
    try:
        rsi = get_stock_rsi(ticker, use_wilder=True)
        if rsi != rsi:  # NaN 체크
            return None
        return {
            "ticker": ticker,
            "rsi": float(rsi)
        }
    except Exception as e:
        print(f"Error calculating RSI for {ticker}: {e}")
        return None

def analyze_sar_macd(ticker):
    """2차, 3차 필터링: SAR + MACD 분석"""
    try:
        # SAR 분석
        sar_result = get_stock_sar_signal(ticker)
        
        # MACD 분석
        macd_result = get_stock_macd_signal(ticker)
        
        return {
            "sar_signal": sar_result["signal"],
            "sar_trend": sar_result["trend"],
            "sar_strength": sar_result["strength"],
            "current_open": sar_result["current_open"],
            "current_sar": sar_result["current_sar"],
            "macd": macd_result["macd"],
            "macd_signal": macd_result["signal"],
            "macd_histogram": macd_result["histogram"],
            "macd_golden_cross": macd_result["golden_cross"],
            "macd_golden_today": macd_result["golden_cross_today"]
        }
    except Exception as e:
        print(f"Error analyzing SAR/MACD for {ticker}: {e}")
        return None

def main():
    # 명령행 인자 파싱
    parser = argparse.ArgumentParser(description='RSI → SAR → MACD 순차 필터링 스크리닝')
    parser.add_argument('--rsi-max', type=float, default=30.0, 
                       help='RSI 최대값 (기본값: 30.0, 과매도 기준)')
    parser.add_argument('--workers', type=int, default=4,
                       help='멀티프로세싱 워커 수 (기본값: 4)')
    parser.add_argument('--output', type=str, default='data/rsi_sar_macd_screening.json',
                       help='결과 저장 파일 경로')
    parser.add_argument('--telegram', action='store_true',
                       help='텔레그램으로 결과 전송')
    parser.add_argument('--market', type=str, default='ALL',
                       choices=['ALL', 'KOSPI', 'KOSDAQ', 'KONEX'],
                       help='분석할 시장 (기본값: ALL)')
    
    args = parser.parse_args()
    
    rsi_threshold = args.rsi_max
    target_market = args.market
    
    print(f"=== RSI < {rsi_threshold} → SAR → MACD 순차 필터링 시작 ===")
    print(f"📊 대상 시장: {target_market}")
    
    # 조건 설명
    if rsi_threshold <= 30:
        condition_desc = "과매도"
    elif rsi_threshold <= 40:
        condition_desc = "약간 과매도"
    elif rsi_threshold <= 50:
        condition_desc = "중립~과매도"
    else:
        condition_desc = "완화된 조건"
    
    print(f"📊 1차 필터 조건: RSI < {rsi_threshold} ({condition_desc})")
    
    # KRX 상장 종목 리스트 가져오기 (시장별 필터링)
    print(f"KRX {target_market} 상장 종목 리스트를 가져오는 중...")
    tickers = stock.get_market_ticker_list(market=target_market)
    print(f"총 {len(tickers)}개 종목")
    
    start_all = time.time()
    now_dt = datetime.datetime.now()
    analysis_time_str = now_dt.strftime('%m월 %d일 %H:%M 기준')
    
    # 1차 필터링: 모든 종목의 RSI 계산
    print("1차 필터링: 모든 종목 RSI 계산 중...")
    start_rsi = time.time()
    rsi_results = []
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        future_to_ticker = {executor.submit(analyze_rsi_only, ticker): ticker for ticker in tickers}
        for future in tqdm(as_completed(future_to_ticker), total=len(tickers), desc="RSI 계산"):
            result = future.result()
            if result:
                rsi_results.append(result)
    end_rsi = time.time()
    rsi_time = end_rsi - start_rsi
    print(f"RSI 계산 완료: {len(rsi_results)}개 종목 ({rsi_time:.1f}초 소요)")
    
    # RSI 임계값 필터링
    oversold_stocks = [s for s in rsi_results if s["rsi"] < rsi_threshold]
    print(f"1차 필터링 결과 (RSI < {rsi_threshold}): {len(oversold_stocks)}개 종목")
    if len(oversold_stocks) == 0:
        print(f"❌ RSI < {rsi_threshold}인 종목이 없습니다.")
        print(f"💡 조건을 완화해보세요: --rsi-max 40 또는 --rsi-max 50")
        return
    
    # 종목명 추가
    print("종목명 정보를 추가하는 중...")
    for stock_info in tqdm(oversold_stocks, desc="종목명 추가"):
        try:
            name = stock.get_market_ticker_name(stock_info["ticker"])
            stock_info["name"] = name
        except:
            stock_info["name"] = "N/A"
    
    # 2차, 3차 필터링: RSI 조건 만족 종목들의 SAR + MACD 분석
    print(f"2차, 3차 필터링: {len(oversold_stocks)}개 종목의 SAR + MACD 분석 중...")
    start_sar_macd = time.time()
    oversold_tickers = [s["ticker"] for s in oversold_stocks]
    sar_macd_results = {}
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        future_to_ticker = {executor.submit(analyze_sar_macd, ticker): ticker for ticker in oversold_tickers}
        for future in tqdm(as_completed(future_to_ticker), total=len(oversold_tickers), desc="SAR+MACD 분석"):
            ticker = future_to_ticker[future]
            result = future.result()
            if result:
                sar_macd_results[ticker] = result
    end_sar_macd = time.time()
    sar_macd_time = end_sar_macd - start_sar_macd
    
    # 결과 병합
    final_results = []
    for stock_info in oversold_stocks:
        ticker = stock_info["ticker"]
        if ticker in sar_macd_results:
            merged = {**stock_info, **sar_macd_results[ticker]}
            final_results.append(merged)
    
    # 2차 필터링: SAR 매수 신호
    sar_buy_signals = [s for s in final_results if s["sar_signal"] == 1]
    print(f"2차 필터링 결과 (SAR 매수 신호): {len(sar_buy_signals)}개 종목")
    
    # 3차 필터링: MACD 골든크로스
    golden_cross_stocks = [s for s in sar_buy_signals if s["macd_golden_cross"]]
    print(f"3차 필터링 결과 (MACD 골든크로스): {len(golden_cross_stocks)}개 종목")
    
    # 트리플 강한 신호
    triple_signal_stocks = [s for s in golden_cross_stocks if s["sar_strength"] == "강함"]
    print(f"트리플 강한 신호: {len(triple_signal_stocks)}개 종목")
    
    end_all = time.time()
    total_time = end_all - start_all
    
    # 결과 정렬 (RSI 낮은 순)
    oversold_stocks.sort(key=lambda x: x["rsi"])
    final_results.sort(key=lambda x: x["rsi"])
    sar_buy_signals.sort(key=lambda x: x["rsi"])
    golden_cross_stocks.sort(key=lambda x: x["rsi"])
    triple_signal_stocks.sort(key=lambda x: x["rsi"])
    
    # 시장별 결과 분리
    market_results = {
        "KOSPI": {"oversold": [], "sar_buy": [], "golden_cross": [], "triple": []},
        "KOSDAQ": {"oversold": [], "sar_buy": [], "golden_cross": [], "triple": []},
        "KONEX": {"oversold": [], "sar_buy": [], "golden_cross": [], "triple": []}
    }
    
    # 시장별로 분류 (한 번에 처리)
    print("시장별 결과 분류 중...")
    
    # 모든 결과 리스트를 한 번에 처리
    all_results = [
        ("oversold", oversold_stocks),
        ("sar_buy", sar_buy_signals),
        ("golden_cross", golden_cross_stocks),
        ("triple", triple_signal_stocks)
    ]
    
    for category, stock_list in all_results:
        for stock_info in stock_list:
            market = get_stock_market(stock_info["ticker"])
            if market in market_results:
                market_results[market][category].append(stock_info)
    
    # JSON 저장
    output = {
        "analysis_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "analysis_time_str": analysis_time_str,
        "target_market": target_market,
        "rsi_threshold": rsi_threshold,
        "condition_description": condition_desc,
        "total_stocks": len(tickers),
        "oversold_count": len(oversold_stocks),
        "sar_buy_count": len(sar_buy_signals),
        "golden_cross_count": len(golden_cross_stocks),
        "triple_signal_count": len(triple_signal_stocks),
        "oversold_stocks": oversold_stocks[:50],
        "sar_buy_signals": sar_buy_signals,
        "golden_cross_stocks": golden_cross_stocks,
        "triple_signal_stocks": triple_signal_stocks,
        "market_results": market_results,
        "timing": {
            "rsi_time": rsi_time,
            "sar_macd_time": sar_macd_time,
            "total_time": total_time
        },
        "counts": {
            "rsi": len(rsi_results),
            "oversold": len(oversold_stocks),
            "sar_buy": len(sar_buy_signals),
            "golden_cross": len(golden_cross_stocks),
            "triple": len(triple_signal_stocks)
        }
    }
    
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n결과가 {args.output}에 저장되었습니다.")
    
    # 텔레그램 알림 전송
    if args.telegram:
        if TELEGRAM_AVAILABLE:
            print("\n📱 텔레그램으로 결과를 전송하는 중...")
            try:
                # 최종 필터링 결과 (RSI + SAR + MACD)를 텔레그램으로 전송
                success = send_screening_results_sync(golden_cross_stocks, rsi_threshold, output)
                if success:
                    print("✅ 텔레그램 전송 완료!")
                else:
                    print("❌ 텔레그램 전송 실패")
            except Exception as e:
                print(f"❌ 텔레그램 전송 중 오류: {e}")
        else:
            print("❌ 텔레그램 알림 기능을 사용할 수 없습니다.")
    
    # 통계 요약
    print(f"\n=== 순차 필터링 결과 요약 (RSI < {rsi_threshold}) ===")
    print(f"대상 시장: {target_market}")
    print(f"전체 종목: {len(tickers)}개")
    print(f"1차 (RSI < {rsi_threshold}): {len(oversold_stocks)}개 ({len(oversold_stocks)/len(tickers)*100:.1f}%)")
    if len(oversold_stocks) > 0:
        print(f"2차 (+ SAR 매수): {len(sar_buy_signals)}개 ({len(sar_buy_signals)/len(oversold_stocks)*100:.1f}%)")
        if len(sar_buy_signals) > 0:
            print(f"3차 (+ MACD 골든크로스): {len(golden_cross_stocks)}개 ({len(golden_cross_stocks)/len(sar_buy_signals)*100:.1f}%)")
    
    if len(golden_cross_stocks) > 0:
        print(f"\n🎯 투자 추천: {len(golden_cross_stocks)}개 종목이 모든 조건을 만족합니다!")
    elif len(sar_buy_signals) > 0:
        print(f"\n📈 관심 종목: {len(sar_buy_signals)}개 종목이 RSI + SAR 조건을 만족합니다!")
    else:
        print(f"\n📊 현재 시장에서는 RSI < {rsi_threshold} 조건을 만족하는 매수 기회가 없습니다.")
        if rsi_threshold <= 35:
            print(f"💡 조건 완화 제안: --rsi-max 40 또는 --rsi-max 50")

def get_stock_market(ticker):
    """종목의 시장 정보 조회 (캐시 사용)"""
    global _market_cache
    
    # 캐시가 비어있으면 한 번만 로드
    if not _market_cache:
        try:
            print("시장 데이터를 로딩 중...")
            kospi_tickers = set(stock.get_market_ticker_list(market="KOSPI"))
            kosdaq_tickers = set(stock.get_market_ticker_list(market="KOSDAQ"))
            konex_tickers = set(stock.get_market_ticker_list(market="KONEX"))
            
            _market_cache = {
                "KOSPI": kospi_tickers,
                "KOSDAQ": kosdaq_tickers,
                "KONEX": konex_tickers
            }
            print("✅ 시장 데이터 로딩 완료")
        except Exception as e:
            print(f"❌ 시장 데이터 로딩 실패: {e}")
            return "UNKNOWN"
    
    # 캐시에서 조회
    try:
        if ticker in _market_cache["KOSPI"]:
            return "KOSPI"
        elif ticker in _market_cache["KOSDAQ"]:
            return "KOSDAQ"
        elif ticker in _market_cache["KONEX"]:
            return "KONEX"
        else:
            return "UNKNOWN"
    except:
        return "UNKNOWN"

if __name__ == "__main__":
    main() 