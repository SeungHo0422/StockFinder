// StockFinder Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // 시장 통계 로드
    loadMarketStats();
    
    // 최근 스크리닝 결과 로드
    loadLatestResults();
    
    // 애니메이션 효과
    animateElements();
});

// 시장별 통계 로드
async function loadMarketStats() {
    try {
        const response = await fetch('/api/market-stats');
        const stats = await response.json();
        
        if (stats.error) {
            console.error('시장 통계 로드 실패:', stats.error);
            return;
        }
        
        // 통계 업데이트
        document.getElementById('kospi-count').textContent = stats.KOSPI?.count?.toLocaleString() || '-';
        document.getElementById('kosdaq-count').textContent = stats.KOSDAQ?.count?.toLocaleString() || '-';
        document.getElementById('konex-count').textContent = stats.KONEX?.count?.toLocaleString() || '-';
        document.getElementById('total-count').textContent = stats.ALL?.count?.toLocaleString() || '-';
        
    } catch (error) {
        console.error('시장 통계 로드 중 오류:', error);
    }
}

// 최근 스크리닝 결과 로드
async function loadLatestResults() {
    try {
        const response = await fetch('/api/screening-status');
        const data = await response.json();
        
        const resultsContainer = document.getElementById('latest-results');
        
        if (data.has_results) {
            const marketName = getMarketDisplayName(data.target_market);
            const conditionDesc = getConditionDescription(data.rsi_threshold);
            
            resultsContainer.innerHTML = `
                <div class="row">
                    <div class="col-md-6">
                        <div class="card bg-light">
                            <div class="card-body text-center">
                                <div class="stats-number text-primary">${data.golden_cross_count}</div>
                                <div class="stats-label">최종 선택 종목</div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card bg-light">
                            <div class="card-body text-center">
                                <div class="stats-number text-success">${data.sar_buy_count}</div>
                                <div class="stats-label">SAR 매수 신호</div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="mt-3">
                    <div class="row">
                        <div class="col-md-6">
                            <small class="text-secondary">
                                <i class="fas fa-chart-line me-1"></i>
                                조건: RSI < ${data.rsi_threshold} (${conditionDesc})
                            </small>
                        </div>
                        <div class="col-md-6">
                            <small class="text-secondary">
                                <i class="fas fa-filter me-1"></i>
                                대상: ${marketName}
                            </small>
                        </div>
                    </div>
                    <div class="mt-2">
                        <small class="text-secondary">
                            <i class="fas fa-clock me-1"></i>
                            분석 시점: ${formatDateTime(data.last_update)}
                        </small>
                    </div>
                </div>
                <div class="mt-3">
                    <a href="/results" class="btn btn-primary btn-sm">
                        <i class="fas fa-eye me-1"></i>상세 결과 보기
                    </a>
                </div>
            `;
        } else {
            resultsContainer.innerHTML = `
                <div class="text-center py-4">
                    <i class="fas fa-inbox fa-3x text-secondary mb-3"></i>
                    <p class="text-secondary">아직 스크리닝 결과가 없습니다.</p>
                    <a href="/screening" class="btn btn-primary">
                        <i class="fas fa-play me-1"></i>첫 스크리닝 시작
                    </a>
                </div>
            `;
        }
        
    } catch (error) {
        console.error('최근 결과 로드 중 오류:', error);
        document.getElementById('latest-results').innerHTML = `
            <div class="text-center py-4">
                <i class="fas fa-exclamation-triangle fa-3x text-warning mb-3"></i>
                <p class="text-secondary">결과를 불러오는 중 오류가 발생했습니다.</p>
            </div>
        `;
    }
}

// 시장 표시명 변환
function getMarketDisplayName(market) {
    const marketMap = {
        'ALL': '전체 시장',
        'KOSPI': '코스피',
        'KOSDAQ': '코스닥',
        'KONEX': '코넥스'
    };
    return marketMap[market] || market;
}

// 조건 설명 변환
function getConditionDescription(rsiThreshold) {
    if (rsiThreshold <= 25) return '강한 과매도';
    if (rsiThreshold <= 30) return '과매도';
    if (rsiThreshold <= 35) return '약간 과매도';
    if (rsiThreshold <= 40) return '중립~과매도';
    return '완화된 조건';
}

// 날짜/시간 포맷팅
function formatDateTime(dateString) {
    if (!dateString) return '-';
    
    try {
        const date = new Date(dateString);
        return date.toLocaleString('ko-KR', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch (error) {
        return dateString;
    }
}

// 애니메이션 효과
function animateElements() {
    // 스크롤 애니메이션
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    }, observerOptions);
    
    // 애니메이션 대상 요소들
    document.querySelectorAll('.card, .stats-card').forEach(el => {
        observer.observe(el);
    });
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