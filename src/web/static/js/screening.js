// StockFinder Screening JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // 폼 제출 이벤트 리스너
    const form = document.getElementById('screening-form');
    form.addEventListener('submit', handleScreeningSubmit);
    
    // 시장 선택 변경 시 예상 시간 업데이트
    const marketSelect = document.getElementById('market');
    marketSelect.addEventListener('change', updateEstimatedTime);
    
    // RSI 임계값 변경 시 예상 시간 업데이트
    const rsiSelect = document.getElementById('rsi-threshold');
    rsiSelect.addEventListener('change', updateEstimatedTime);
    
    // 초기 예상 시간 설정
    updateEstimatedTime();
});

// 스크리닝 제출 처리
async function handleScreeningSubmit(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    
    // 버튼 비활성화
    const submitBtn = document.getElementById('run-screening-btn');
    const originalText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>스크리닝 실행 중...';
    
    try {
        // 스크리닝 실행 요청
        const response = await fetch('/api/run-screening', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message, 'success');
            showProgressCard();
            startProgressMonitoring();
        } else {
            showAlert(result.message, 'danger');
        }
        
    } catch (error) {
        console.error('스크리닝 실행 중 오류:', error);
        showAlert('스크리닝 실행 중 오류가 발생했습니다.', 'danger');
    } finally {
        // 버튼 복원
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
    }
}

// 예상 시간 업데이트
async function updateEstimatedTime() {
    const market = document.getElementById('market').value;
    const rsiThreshold = document.getElementById('rsi-threshold').value;
    
    try {
        // 시장별 종목 수 가져오기
        const response = await fetch('/api/market-stats');
        const stats = await response.json();
        
        if (stats.error) {
            console.error('시장 통계 로드 실패:', stats.error);
            return;
        }
        
        const stockCount = stats[market]?.count || 0;
        const estimatedTime = calculateEstimatedTime(stockCount, rsiThreshold);
        
        // UI 업데이트
        document.getElementById('estimated-stocks').textContent = stockCount.toLocaleString();
        document.getElementById('estimated-time').textContent = estimatedTime;
        
    } catch (error) {
        console.error('예상 시간 계산 중 오류:', error);
    }
}

// 예상 시간 계산
function calculateEstimatedTime(stockCount, rsiThreshold) {
    // 기본 계산 로직 (실제 성능에 따라 조정 필요)
    const rsiTime = stockCount * 0.01; // RSI 계산 시간 (초)
    const oversoldRatio = Math.max(0.05, Math.min(0.3, (50 - rsiThreshold) / 50)); // 과매도 비율
    const oversoldCount = Math.floor(stockCount * oversoldRatio);
    const sarMacdTime = oversoldCount * 0.1; // SAR+MACD 분석 시간 (초)
    
    const totalSeconds = rsiTime + sarMacdTime;
    
    if (totalSeconds < 60) {
        return Math.ceil(totalSeconds) + '초';
    } else if (totalSeconds < 3600) {
        return Math.ceil(totalSeconds / 60) + '분';
    } else {
        return Math.ceil(totalSeconds / 3600) + '시간';
    }
}

// 진행 상황 카드 표시
function showProgressCard() {
    const progressCard = document.getElementById('progress-card');
    progressCard.style.display = 'block';
    progressCard.scrollIntoView({ behavior: 'smooth' });
}

// 진행 상황 모니터링 시작
function startProgressMonitoring() {
    let progress = 0;
    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-text');
    
    const stages = [
        'RSI 계산 중...',
        '과매도 종목 필터링 중...',
        'SAR 분석 중...',
        'MACD 분석 중...',
        '결과 정리 중...',
        '완료!'
    ];
    
    const interval = setInterval(() => {
        progress += Math.random() * 15;
        
        if (progress >= 100) {
            progress = 100;
            clearInterval(interval);
            
            // 완료 후 결과 페이지로 리다이렉트
            setTimeout(() => {
                window.location.href = '/results';
            }, 2000);
        }
        
        progressBar.style.width = progress + '%';
        
        const stageIndex = Math.floor((progress / 100) * (stages.length - 1));
        progressText.textContent = stages[stageIndex];
        
    }, 2000);
    
    // 실제 진행 상황 확인 (30초마다)
    const statusCheckInterval = setInterval(async () => {
        try {
            const response = await fetch('/api/screening-status');
            const data = await response.json();
            
            if (data.has_results) {
                clearInterval(statusCheckInterval);
                clearInterval(interval);
                
                progressBar.style.width = '100%';
                progressText.textContent = '완료!';
                
                setTimeout(() => {
                    window.location.href = '/results';
                }, 1000);
            }
        } catch (error) {
            console.error('상태 확인 중 오류:', error);
        }
    }, 30000);
}

// 알림 표시 함수
function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alert-container');
    const alertId = 'alert-' + Date.now();
    
    const alertHtml = `
        <div id="${alertId}" class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    alertContainer.insertAdjacentHTML('beforeend', alertHtml);
    
    // 5초 후 자동 제거
    setTimeout(() => {
        const alert = document.getElementById(alertId);
        if (alert) {
            alert.remove();
        }
    }, 5000);
}

// 폼 유효성 검사
function validateForm() {
    const rsiThreshold = document.getElementById('rsi-threshold').value;
    const market = document.getElementById('market').value;
    
    if (!rsiThreshold || !market) {
        showAlert('모든 필드를 입력해주세요.', 'warning');
        return false;
    }
    
    const rsiValue = parseFloat(rsiThreshold);
    if (rsiValue < 20 || rsiValue > 60) {
        showAlert('RSI 임계값은 20-60 사이로 설정해주세요.', 'warning');
        return false;
    }
    
    return true;
}

// 시장별 설명 업데이트
function updateMarketDescription() {
    const market = document.getElementById('market').value;
    const descriptions = {
        'ALL': '전체 시장 (코스피 + 코스닥 + 코넥스) - 모든 상장 종목을 분석합니다.',
        'KOSPI': '코스피 - 대형주 중심의 안정적인 종목들을 분석합니다.',
        'KOSDAQ': '코스닥 - 중소형주와 IT 기업들을 중심으로 분석합니다.',
        'KONEX': '코넥스 - 벤처기업과 스타트업을 중심으로 분석합니다.'
    };
    
    // 설명 업데이트 로직 (필요시 구현)
    console.log('선택된 시장:', market, descriptions[market]);
} 