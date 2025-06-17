#!/usr/bin/env python3
"""
텔레그램 봇 기능 테스트 스크립트
"""

import os
import sys
import json
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_telegram_bot_import():
    """텔레그램 봇 모듈 import 테스트"""
    try:
        from src.notifier.telegram_bot import TelegramNotifier, send_test_message_sync
        print("✅ 텔레그램 봇 모듈 import 성공")
        return True
    except ImportError as e:
        print(f"❌ 텔레그램 봇 모듈 import 실패: {e}")
        return False

def test_telegram_bot_initialization():
    """텔레그램 봇 초기화 테스트"""
    try:
        # 환경변수 설정 (테스트용)
        os.environ['TELEGRAM_BOT_TOKEN'] = 'test_token_123'
        os.environ['TELEGRAM_CHAT_ID'] = 'test_chat_456'
        
        from src.notifier.telegram_bot import TelegramNotifier
        
        notifier = TelegramNotifier()
        print("✅ 텔레그램 봇 초기화 성공")
        print(f"   - Bot Token: {notifier.bot_token}")
        print(f"   - Chat ID: {notifier.chat_id}")
        return True
    except Exception as e:
        print(f"❌ 텔레그램 봇 초기화 실패: {e}")
        return False

def test_message_formatting():
    """메시지 포맷팅 테스트"""
    try:
        from src.notifier.telegram_bot import TelegramNotifier
        
        # 테스트 데이터
        test_results = [
            {
                "name": "삼성전자",
                "ticker": "005930",
                "rsi": 25.34,
                "current_open": 75000,
                "sar_trend": "상승",
                "sar_strength": "강함",
                "macd": 0.45,
                "macd_golden_today": True
            },
            {
                "name": "SK하이닉스",
                "ticker": "000660",
                "rsi": 28.12,
                "current_open": 125000,
                "sar_trend": "상승",
                "sar_strength": "중간",
                "macd": 0.23,
                "macd_golden_today": False
            }
        ]
        
        notifier = TelegramNotifier()
        message = notifier.format_screening_results(test_results, 30.0)
        
        print("✅ 메시지 포맷팅 성공")
        print("📱 생성된 메시지:")
        print("-" * 50)
        print(message)
        print("-" * 50)
        return True
    except Exception as e:
        print(f"❌ 메시지 포맷팅 실패: {e}")
        return False

def test_scheduler_import():
    """스케줄러 모듈 import 테스트"""
    try:
        from src.notifier.scheduler import ScreeningScheduler, test_telegram_connection
        print("✅ 스케줄러 모듈 import 성공")
        return True
    except ImportError as e:
        print(f"❌ 스케줄러 모듈 import 실패: {e}")
        return False

def test_screening_integration():
    """스크리닝 통합 테스트"""
    try:
        # 기존 스크리닝 스크립트에 텔레그램 기능이 추가되었는지 확인
        with open('calc_rsi_sar_screening.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        if '--telegram' in content and 'send_screening_results_sync' in content:
            print("✅ 스크리닝 스크립트에 텔레그램 기능 통합됨")
            return True
        else:
            print("❌ 스크리닝 스크립트에 텔레그램 기능이 통합되지 않음")
            return False
    except Exception as e:
        print(f"❌ 스크리닝 통합 테스트 실패: {e}")
        return False

def main():
    """메인 테스트 함수"""
    print("🧪 텔레그램 봇 기능 테스트 시작")
    print("=" * 50)
    
    tests = [
        ("텔레그램 봇 모듈 Import", test_telegram_bot_import),
        ("텔레그램 봇 초기화", test_telegram_bot_initialization),
        ("메시지 포맷팅", test_message_formatting),
        ("스케줄러 모듈 Import", test_scheduler_import),
        ("스크리닝 통합", test_screening_integration),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name} 테스트 중...")
        if test_func():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 테스트 결과: {passed}/{total} 통과")
    
    if passed == total:
        print("🎉 모든 테스트가 성공했습니다!")
        print("\n📋 다음 단계:")
        print("1. 텔레그램에서 @BotFather로 봇 생성")
        print("2. @userinfobot에서 Chat ID 확인")
        print("3. .env 파일에 토큰과 Chat ID 설정")
        print("4. python src/notifier/scheduler.py --test 로 실제 연결 테스트")
    else:
        print("⚠️  일부 테스트가 실패했습니다. 문제를 확인해주세요.")
    
    return passed == total

if __name__ == "__main__":
    main() 