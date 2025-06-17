import os
import sys
import json
import time
import logging
import schedule
from datetime import datetime, timedelta
from typing import List, Dict, Any
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.notifier.telegram_bot import TelegramNotifier, send_test_message_sync, send_screening_results_sync
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class ScreeningScheduler:
    """스크리닝 스케줄러 클래스"""
    
    def __init__(self, rsi_threshold: float = 30.0, run_time: str = "09:30", market: str = "ALL"):
        """
        스케줄러 초기화
        
        Args:
            rsi_threshold: RSI 임계값 (기본값: 30.0)
            run_time: 매일 실행할 시간 (기본값: "09:30")
            market: 대상 시장 (기본값: "ALL")
        """
        self.rsi_threshold = rsi_threshold
        self.run_time = run_time
        self.market = market
        self.telegram_notifier = TelegramNotifier()
        
    def run_screening(self) -> List[Dict[str, Any]]:
        """
        스크리닝 실행
        
        Returns:
            List[Dict[str, Any]]: 스크리닝 결과
        """
        try:
            logger.info(f"스크리닝 시작: RSI < {self.rsi_threshold}")
            
            # calc_rsi_sar_screening.py의 main 함수 로직을 여기서 실행
            # 실제로는 해당 모듈을 import해서 사용하는 것이 좋지만,
            # 여기서는 간단히 결과 파일을 읽어오는 방식으로 구현
            
            result_file = f"data/rsi_sar_macd_screening_rsi{self.rsi_threshold}.json"
            
            if os.path.exists(result_file):
                with open(result_file, 'r', encoding='utf-8') as f:
                    results = json.load(f)
                logger.info(f"스크리닝 완료: {len(results)}개 종목 발견")
                return results
            else:
                logger.warning(f"결과 파일이 없습니다: {result_file}")
                return []
                
        except Exception as e:
            logger.error(f"스크리닝 실행 중 오류 발생: {e}")
            return []
    
    async def send_daily_report(self):
        """일일 리포트 전송"""
        try:
            logger.info("일일 스크리닝 리포트 전송 시작")
            
            # 스크리닝 실행
            results = self.run_screening()
            
            # 텔레그램으로 결과 전송
            success = await self.telegram_notifier.send_screening_results(results, self.rsi_threshold)
            
            if success:
                logger.info("일일 스크리닝 리포트 전송 완료")
            else:
                logger.error("일일 스크리닝 리포트 전송 실패")
                
        except Exception as e:
            logger.error(f"일일 리포트 전송 중 오류 발생: {e}")
    
    def schedule_daily_screening(self):
        """매일 스크리닝 스케줄 설정"""
        schedule.every().day.at(self.run_time).do(self._run_daily_task)
        logger.info(f"매일 {self.run_time}에 스크리닝 스케줄 설정 완료")
    
    def _run_daily_task(self):
        """일일 작업 실행 (스케줄러용)"""
        import asyncio
        asyncio.run(self.send_daily_report())
    
    def run_scheduler(self):
        """스케줄러 실행"""
        logger.info("스크리닝 스케줄러 시작")
        logger.info(f"설정: RSI 임계값={self.rsi_threshold}, 실행시간={self.run_time}, 시장={self.market}")
        
        # 스케줄 설정
        self.schedule_daily_screening()
        
        # 스케줄러 루프 실행
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # 1분마다 체크
            except KeyboardInterrupt:
                logger.info("스케줄러 종료")
                break
            except Exception as e:
                logger.error(f"스케줄러 실행 중 오류: {e}")
                time.sleep(60)

def run_screening_and_send(rsi_threshold: float = 30.0, market: str = "ALL") -> bool:
    """
    스크리닝을 실행하고 텔레그램으로 결과를 전송 (즉시 실행)
    
    Args:
        rsi_threshold: RSI 임계값
        market: 대상 시장
        
    Returns:
        bool: 성공 여부
    """
    try:
        logger.info(f"즉시 스크리닝 실행: RSI < {rsi_threshold}, 시장: {market}")
        
        # 실제 스크리닝 실행
        import subprocess
        import sys
        
        # calc_rsi_sar_screening.py 실행 (시장별 필터링 추가)
        cmd = [sys.executable, 'calc_rsi_sar_screening.py', '--rsi-max', str(rsi_threshold), '--market', market, '--workers', '4']
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"스크리닝 실행 실패: {result.stderr}")
            return False
        
        logger.info("스크리닝 실행 완료")
        
        # 결과 파일에서 golden_cross_stocks 읽기
        result_file = f"data/rsi_sar_macd_screening.json"
        
        if not os.path.exists(result_file):
            logger.warning(f"결과 파일이 없습니다: {result_file}")
            return False
        
        with open(result_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        golden_cross_stocks = data.get('golden_cross_stocks', [])
        meta = {
            'timing': data.get('timing', {}),
            'counts': data.get('counts', {}),
            'analysis_time_str': data.get('analysis_time_str', None),
            'target_market': data.get('target_market', market),
            'market_results': data.get('market_results', {})
        }
        
        # 텔레그램으로 결과 전송
        success = send_screening_results_sync(golden_cross_stocks, rsi_threshold, meta)
        
        if success:
            logger.info("즉시 스크리닝 결과 전송 완료")
        else:
            logger.error("즉시 스크리닝 결과 전송 실패")
            
        return success
        
    except Exception as e:
        logger.error(f"즉시 스크리닝 실행 중 오류: {e}")
        return False

def test_telegram_connection() -> bool:
    """
    텔레그램 연결 테스트
    
    Returns:
        bool: 연결 성공 여부
    """
    try:
        logger.info("텔레그램 연결 테스트 시작")
        success = send_test_message_sync()
        
        if success:
            logger.info("텔레그램 연결 테스트 성공")
        else:
            logger.error("텔레그램 연결 테스트 실패")
            
        return success
        
    except Exception as e:
        logger.error(f"텔레그램 연결 테스트 중 오류: {e}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='스크리닝 스케줄러')
    parser.add_argument('--rsi-threshold', type=float, default=30.0,
                       help='RSI 임계값 (기본값: 30.0)')
    parser.add_argument('--run-time', type=str, default='09:30',
                       help='매일 실행할 시간 (기본값: 09:30)')
    parser.add_argument('--market', type=str, default='ALL',
                       choices=['ALL', 'KOSPI', 'KOSDAQ', 'KONEX'],
                       help='분석할 시장 (기본값: ALL)')
    parser.add_argument('--test', action='store_true',
                       help='텔레그램 연결 테스트')
    parser.add_argument('--run-now', action='store_true',
                       help='즉시 스크리닝 실행 및 전송')
    
    args = parser.parse_args()
    
    if args.test:
        test_telegram_connection()
    elif args.run_now:
        run_screening_and_send(args.rsi_threshold, args.market)
    else:
        scheduler = ScreeningScheduler(args.rsi_threshold, args.run_time, args.market)
        scheduler.run_scheduler() 