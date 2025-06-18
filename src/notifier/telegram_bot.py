import os
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from telegram import Bot
from telegram.error import TelegramError
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramNotifier:
    """텔레그램을 통한 스크리닝 결과 알림 클래스"""
    
    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        """
        텔레그램 노티파이어 초기화
        
        Args:
            bot_token: 텔레그램 봇 토큰 (환경변수 TELEGRAM_BOT_TOKEN에서도 읽음)
            chat_id: 채팅 ID (환경변수 TELEGRAM_CHAT_ID에서도 읽음)
        """
        self.bot_token = bot_token or os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = chat_id or os.getenv('TELEGRAM_CHAT_ID')
        
        # 봇 토큰에서 주석 제거 (# 이후 텍스트 제거)
        if self.bot_token and '#' in self.bot_token:
            self.bot_token = self.bot_token.split('#')[0].strip()
            logger.info("봇 토큰에서 주석을 제거했습니다.")
        
        # 채팅 ID에서 주석 제거
        if self.chat_id and '#' in self.chat_id:
            self.chat_id = self.chat_id.split('#')[0].strip()
            logger.info("채팅 ID에서 주석을 제거했습니다.")
        
        if not self.bot_token:
            raise ValueError("텔레그램 봇 토큰이 필요합니다. TELEGRAM_BOT_TOKEN 환경변수를 설정하거나 bot_token 파라미터를 전달하세요.")
        
        if not self.chat_id:
            raise ValueError("텔레그램 채팅 ID가 필요합니다. TELEGRAM_CHAT_ID 환경변수를 설정하거나 chat_id 파라미터를 전달하세요.")
        
        self.bot = Bot(token=self.bot_token)
        
    async def send_message(self, message: str, parse_mode: str = 'HTML') -> bool:
        """
        텔레그램으로 메시지 전송
        
        Args:
            message: 전송할 메시지
            parse_mode: 메시지 파싱 모드 ('HTML', 'Markdown' 등)
            
        Returns:
            bool: 전송 성공 여부
        """
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=parse_mode
            )
            logger.info("텔레그램 메시지 전송 성공")
            return True
        except TelegramError as e:
            logger.error(f"텔레그램 메시지 전송 실패: {e}")
            return False
    
    def format_screening_results(self, results: List[Dict[str, Any]], rsi_threshold: float, meta: dict = None) -> str:
        """
        스크리닝 결과를 텔레그램 메시지 형식으로 포맷팅
        Args:
            results: 스크리닝 결과 리스트
            rsi_threshold: RSI 임계값
            meta: timing/counts/analysis_time_str/market_results 등 부가정보 dict
        Returns:
            str: 포맷팅된 메시지
        """
        # 날짜/시간 정보
        if meta and meta.get('analysis_time_str'):
            time_str = meta['analysis_time_str']
        else:
            time_str = datetime.now().strftime('%m월 %d일 %H:%M 기준')
        
        # 대상 시장 정보
        target_market = meta.get('target_market', 'ALL') if meta else 'ALL'
        market_name_map = {
            'ALL': '전체 시장',
            'KOSPI': '코스피',
            'KOSDAQ': '코스닥',
            'KONEX': '코넥스'
        }
        market_display = market_name_map.get(target_market, target_market)
        
        # 조건 설명
        if rsi_threshold <= 30:
            condition_desc = "과매도"
        elif rsi_threshold <= 40:
            condition_desc = "약간 과매도"
        elif rsi_threshold <= 50:
            condition_desc = "중립~과매도"
        else:
            condition_desc = "완화된 조건"
        
        message = f"📊 오늘의 스크리닝 결과 ({time_str})\n"
        message += f"🎯 대상: {market_display}\n"
        message += f"🎯 조건: RSI < {rsi_threshold} ({condition_desc}) + SAR 매수 + MACD 골든크로스\n"
        
        # 과정/소요시간 정보
        if meta and 'timing' in meta and 'counts' in meta:
            t = meta['timing']
            c = meta['counts']
            message += f"\n[진행 요약]\n"
            message += f"1단계: 전체 {c['rsi']}종목 RSI 계산 ({t['rsi_time']:.1f}초) → {c['oversold']}개 과매도\n"
            message += f"2단계: SAR+MACD 분석 ({t['sar_macd_time']:.1f}초) → SAR매수 {c['sar_buy']}개\n"
            message += f"3단계: MACD골든크로스 → 최종 {c['golden_cross']}개\n"
            message += f"총 소요: {t['total_time']:.1f}초\n"
        
        message += f"\n📈 발견된 종목: {len(results)}개\n\n"
        
        if not results:
            message += f"❌ RSI < {rsi_threshold} + SAR 매수 + MACD 골든크로스 조건을 만족하는 종목이 없습니다."
        else:
            # 시장별 결과 분리 표시
            if meta and 'market_results' in meta:
                market_results = meta['market_results']
                message += "🏢 시장별 결과\n"
                message += "=" * 30 + "\n"
                
                for market_code in ['KOSPI', 'KOSDAQ', 'KONEX']:
                    if market_code in market_results:
                        market_data = market_results[market_code]
                        golden_count = len(market_data['golden_cross'])
                        sar_count = len(market_data['sar_buy'])
                        oversold_count = len(market_data['oversold'])
                        
                        if golden_count > 0 or sar_count > 0:
                            market_name = market_name_map.get(market_code, market_code)
                            message += f"\n📊 {market_name}\n"
                            message += f"   과매도: {oversold_count}개\n"
                            message += f"   SAR매수: {sar_count}개\n"
                            message += f"   최종선택: {golden_count}개\n"
                            
                            # 해당 시장의 최종 선택 종목들 표시
                            if golden_count > 0:
                                message += f"   📋 종목:\n"
                                for i, stock in enumerate(market_data['golden_cross'][:3], 1):  # 상위 3개만
                                    name = stock.get('name', 'N/A')
                                    ticker = stock.get('ticker', 'N/A')
                                    rsi = stock.get('rsi', 0)
                                    current_open = stock.get('current_open', 0)
                                    message += f"      {i}. {name} ({ticker})\n"
                                    message += f"         RSI: {rsi:.2f}, 시가: {current_open:,.0f}원\n"
                                if golden_count > 3:
                                    message += f"      ... 외 {golden_count - 3}개\n"
                
                message += "\n" + "=" * 30 + "\n"
            
            # 전체 결과 요약 (상위 5개)
            message += "🏆 전체 최종 선택 종목 (상위 5개)\n"
            for i, stock in enumerate(results[:5], 1):
                name = stock.get('name', 'N/A')
                ticker = stock.get('ticker', 'N/A')
                rsi = stock.get('rsi', 0)
                current_open = stock.get('current_open', 0)
                sar_trend = stock.get('sar_trend', 'N/A')
                sar_strength = stock.get('sar_strength', 'N/A')
                macd = stock.get('macd', 0)
                macd_golden_today = stock.get('macd_golden_today', False)
                
                message += f"\n{i}. {name} ({ticker})\n"
                message += f"   💹 RSI: {rsi:.2f} ({condition_desc})\n"
                message += f"   📈 SAR: {sar_trend} 추세, {sar_strength} 신호\n"
                message += f"   🎯 MACD: {macd:.2f} (골든크로스 ✓)\n"
                message += f"   💰 시가: {current_open:,.0f}원\n"
                
                if macd_golden_today:
                    message += f"   ⭐ 오늘 MACD 골든크로스 발생!\n"
            
            if len(results) > 5:
                message += f"\n... 외 {len(results) - 5}개 종목\n"
        
        message += f"\n🔍 이 결과는 자동으로 생성되었습니다."
        return message
    
    async def send_screening_results(self, results: List[Dict[str, Any]], rsi_threshold: float, meta: dict = None) -> bool:
        """
        스크리닝 결과를 텔레그램으로 전송
        
        Args:
            results: 스크리닝 결과 리스트
            rsi_threshold: RSI 임계값
            meta: timing/counts/analysis_time_str 등 부가정보 dict
            
        Returns:
            bool: 전송 성공 여부
        """
        message = self.format_screening_results(results, rsi_threshold, meta)
        return await self.send_message(message, parse_mode=None)  # HTML 파싱 모드 비활성화
    
    async def send_test_message(self) -> bool:
        """
        테스트 메시지 전송
        
        Returns:
            bool: 전송 성공 여부
        """
        test_message = f"🧪 <b>텔레그램 봇 테스트</b>\n\n✅ 연결이 성공적으로 설정되었습니다!\n📅 {datetime.now().strftime('%Y년 %m월 %d일 %H:%M:%S')}"
        return await self.send_message(test_message)

# 동기 래퍼 함수들 (비동기 함수를 동기적으로 호출할 수 있도록)
def send_message_sync(message: str, parse_mode: str = 'HTML') -> bool:
    """동기적으로 텔레그램 메시지 전송"""
    notifier = TelegramNotifier()
    return asyncio.run(notifier.send_message(message, parse_mode))

def send_screening_results_sync(results: List[Dict[str, Any]], rsi_threshold: float, meta: dict = None) -> bool:
    """동기적으로 스크리닝 결과 전송"""
    notifier = TelegramNotifier()
    return asyncio.run(notifier.send_screening_results(results, rsi_threshold, meta))

def send_test_message_sync() -> bool:
    """동기적으로 테스트 메시지 전송"""
    notifier = TelegramNotifier()
    return asyncio.run(notifier.send_test_message()) 