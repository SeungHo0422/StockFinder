#!/usr/bin/env python3
"""
시장별 종목 분석 테스트 스크립트
"""

from pykrx import stock
import pandas as pd
from datetime import datetime

def analyze_markets():
    """각 시장별 종목 분석"""
    print("=== 시장별 종목 분석 ===")
    print(f"분석 시점: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M:%S')}")
    print()
    
    markets = {
        "KOSPI": "코스피",
        "KOSDAQ": "코스닥", 
        "KONEX": "코넥스",
        "ALL": "전체"
    }
    
    market_stats = {}
    
    for market_code, market_name in markets.items():
        print(f"📊 {market_name} ({market_code}) 분석 중...")
        
        try:
            # 종목 리스트 가져오기
            tickers = stock.get_market_ticker_list(market=market_code)
            
            # 종목명 가져오기
            ticker_names = {}
            for ticker in tickers[:10]:  # 상위 10개만 샘플로
                try:
                    name = stock.get_market_ticker_name(ticker)
                    ticker_names[ticker] = name
                except:
                    ticker_names[ticker] = "N/A"
            
            market_stats[market_code] = {
                "count": len(tickers),
                "name": market_name,
                "sample_tickers": ticker_names
            }
            
            print(f"   ✅ 종목 수: {len(tickers):,}개")
            print(f"   📋 샘플 종목:")
            for ticker, name in list(ticker_names.items())[:5]:
                print(f"      - {ticker}: {name}")
            if len(ticker_names) > 5:
                print(f"      ... 외 {len(ticker_names) - 5}개")
            print()
            
        except Exception as e:
            print(f"   ❌ 오류: {e}")
            print()
    
    # 전체 통계 출력
    print("=== 전체 통계 ===")
    total_count = sum(stats["count"] for stats in market_stats.values() if "count" in stats)
    
    for market_code, stats in market_stats.items():
        if "count" in stats:
            percentage = (stats["count"] / total_count) * 100
            print(f"{stats['name']}: {stats['count']:,}개 ({percentage:.1f}%)")
    
    print(f"\n총 종목 수: {total_count:,}개")
    
    return market_stats

def analyze_market_distribution():
    """시장별 분포 상세 분석"""
    print("\n=== 시장별 분포 상세 분석 ===")
    
    # 각 시장별로 개별 조회
    kospi_tickers = stock.get_market_ticker_list(market="KOSPI")
    kosdaq_tickers = stock.get_market_ticker_list(market="KOSDAQ")
    konex_tickers = stock.get_market_ticker_list(market="KONEX")
    all_tickers = stock.get_market_ticker_list(market="ALL")
    
    print(f"코스피: {len(kospi_tickers):,}개")
    print(f"코스닥: {len(kosdaq_tickers):,}개") 
    print(f"코넥스: {len(konex_tickers):,}개")
    print(f"전체: {len(all_tickers):,}개")
    
    # 중복 확인
    kospi_set = set(kospi_tickers)
    kosdaq_set = set(kosdaq_tickers)
    konex_set = set(konex_tickers)
    all_set = set(all_tickers)
    
    print(f"\n중복 분석:")
    print(f"코스피 ∩ 코스닥: {len(kospi_set & kosdaq_set)}개")
    print(f"코스피 ∩ 코넥스: {len(kospi_set & konex_set)}개")
    print(f"코스닥 ∩ 코넥스: {len(kosdaq_set & konex_set)}개")
    
    # ALL이 실제로 모든 시장의 합집합인지 확인
    union_all = kospi_set | kosdaq_set | konex_set
    print(f"합집합: {len(union_all)}개")
    print(f"ALL과 일치: {union_all == all_set}")

def get_market_info(ticker):
    """특정 종목의 시장 정보 조회"""
    try:
        # 종목명
        name = stock.get_market_ticker_name(ticker)
        
        # 시장 구분 (각 시장별로 확인)
        if ticker in stock.get_market_ticker_list(market="KOSPI"):
            market = "KOSPI"
        elif ticker in stock.get_market_ticker_list(market="KOSDAQ"):
            market = "KOSDAQ"
        elif ticker in stock.get_market_ticker_list(market="KONEX"):
            market = "KONEX"
        else:
            market = "UNKNOWN"
        
        return {
            "ticker": ticker,
            "name": name,
            "market": market
        }
    except Exception as e:
        return {
            "ticker": ticker,
            "name": "N/A",
            "market": "ERROR",
            "error": str(e)
        }

def test_sample_tickers():
    """샘플 종목들의 시장 정보 확인"""
    print("\n=== 샘플 종목 시장 정보 ===")
    
    sample_tickers = ["005930", "000660", "035420", "051910", "006400"]  # 삼성전자, SK하이닉스, NAVER, LG화학, 삼성SDI
    
    for ticker in sample_tickers:
        info = get_market_info(ticker)
        print(f"{ticker}: {info['name']} ({info['market']})")

if __name__ == "__main__":
    # 시장별 종목 분석
    market_stats = analyze_markets()
    
    # 시장별 분포 상세 분석
    analyze_market_distribution()
    
    # 샘플 종목 시장 정보
    test_sample_tickers()
    
    print("\n=== 분석 완료 ===")
    print("현재 스크리닝에서는 'ALL' 시장을 사용하여 모든 시장의 종목을 분석하고 있습니다.") 