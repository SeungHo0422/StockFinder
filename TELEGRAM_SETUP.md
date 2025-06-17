# 텔레그램 봇 설정 가이드

이 가이드는 스크리닝 결과를 텔레그램으로 받기 위한 설정 방법을 설명합니다.

## 1. 텔레그램 봇 생성

### 1.1 BotFather에서 봇 생성
1. 텔레그램에서 [@BotFather](https://t.me/botfather)를 검색
2. `/start` 명령어로 시작
3. `/newbot` 명령어로 새 봇 생성
4. 봇 이름과 사용자명을 입력
5. 봇 토큰을 받아서 저장 (예: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 1.2 봇과 대화 시작
1. 생성된 봇을 검색
2. `/start` 명령어로 대화 시작

## 2. Chat ID 확인

### 2.1 @userinfobot 사용
1. 텔레그램에서 [@userinfobot](https://t.me/userinfobot)을 검색
2. `/start` 명령어로 시작
3. 본인의 Chat ID를 확인 (예: `123456789`)

## 3. 환경변수 설정

### 3.1 .env 파일 생성
프로젝트 루트에 `.env` 파일을 생성하고 다음 내용을 추가:

```bash
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

### 3.2 실제 값으로 교체
- `your_bot_token_here`를 1.1에서 받은 봇 토큰으로 교체
- `your_chat_id_here`를 2.1에서 확인한 Chat ID로 교체

예시:
```bash
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
```

## 4. 사용 방법

### 4.1 즉시 스크리닝 및 텔레그램 전송
```bash
python calc_rsi_sar_screening.py --telegram
```

### 4.2 텔레그램 연결 테스트
```bash
python src/notifier/scheduler.py --test
```

### 4.3 즉시 스크리닝 실행 및 전송
```bash
python src/notifier/scheduler.py --run-now
```

### 4.4 매일 자동 스크리닝 스케줄러 실행
```bash
python src/notifier/scheduler.py --run-time 09:30
```

## 5. 스케줄러 설정

### 5.1 매일 자동 실행
스케줄러는 매일 지정된 시간에 자동으로 스크리닝을 실행하고 텔레그램으로 결과를 전송합니다.

기본 실행 시간: 오전 9시 30분 (장 시작 전)

### 5.2 실행 시간 변경
```bash
python src/notifier/scheduler.py --run-time 10:00
```

### 5.3 RSI 임계값 변경
```bash
python src/notifier/scheduler.py --rsi-threshold 40 --run-time 09:30
```

## 6. 메시지 형식

텔레그램으로 받는 메시지는 다음과 같은 형식입니다:

```
📊 오늘의 스크리닝 결과
📅 2024년 01월 15일
🎯 조건: RSI < 30 (과매도) + SAR 매수 + MACD 골든크로스
📈 발견된 종목: 3개

1. 삼성전자 (005930)
   💹 RSI: 25.34 (과매도)
   📈 SAR: 상승 추세, 강함 신호
   🎯 MACD: 0.45 (골든크로스 ✓)
   💰 현재가: 75,000원

2. SK하이닉스 (000660)
   💹 RSI: 28.12 (과매도)
   📈 SAR: 상승 추세, 중간 신호
   🎯 MACD: 0.23 (골든크로스 ✓)
   💰 현재가: 125,000원

🔍 이 결과는 자동으로 생성되었습니다.
```

## 7. 문제 해결

### 7.1 봇 토큰 오류
- 봇 토큰이 올바른지 확인
- 봇이 활성화되어 있는지 확인

### 7.2 Chat ID 오류
- Chat ID가 올바른지 확인
- 봇과 대화를 시작했는지 확인

### 7.3 메시지 전송 실패
- 인터넷 연결 확인
- 텔레그램 서버 상태 확인
- 봇이 차단되지 않았는지 확인

## 8. 고급 설정

### 8.1 여러 채팅방에 전송
여러 Chat ID를 쉼표로 구분하여 설정:
```bash
TELEGRAM_CHAT_ID=123456789,987654321
```

### 8.2 커스텀 메시지 형식
`src/notifier/telegram_bot.py`의 `format_screening_results` 메서드를 수정하여 메시지 형식을 변경할 수 있습니다.

## 9. 보안 주의사항

- `.env` 파일을 Git에 커밋하지 마세요
- 봇 토큰을 공개하지 마세요
- Chat ID를 공개하지 마세요 