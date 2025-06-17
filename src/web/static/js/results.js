// StockFinder Results JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // 탭 기능 초기화
    initializeTabs();
    
    // 애니메이션 효과
    animateElements();
});

// 탭 기능 초기화
function initializeTabs() {
    // Bootstrap 탭 기능이 자동으로 작동하므로 추가 설정 불필요
    console.log('탭 기능 초기화 완료');
}

// 더보기 토글 기능
function toggleMoreStocks(tableId, totalCount) {
    const tbody = document.getElementById(tableId + '-tbody');
    const button = event.target;
    const isExpanded = button.getAttribute('data-expanded') === 'true';
    
    if (!isExpanded) {
        // 더보기 버튼을 "접기"로 변경
        button.innerHTML = '<i class="fas fa-chevron-up me-1"></i>접기';
        button.setAttribute('data-expanded', 'true');
        
        // 전체 데이터를 표시하는 API 호출 또는 데이터 로드
        loadAllStocks(tableId, totalCount);
    } else {
        // 접기 버튼을 "더보기"로 변경
        const remainingCount = totalCount - 10;
        button.innerHTML = `<i class="fas fa-chevron-down me-1"></i>더보기 (${remainingCount}개)`;
        button.setAttribute('data-expanded', 'false');
        
        // 처음 10개만 표시
        showFirstTenStocks(tableId);
    }
}

// 전체 종목 데이터 로드
async function loadAllStocks(tableId, totalCount) {
    try {
        // 현재 페이지의 데이터를 사용하여 전체 목록 생성
        const response = await fetch('/api/screening-results');
        const data = await response.json();
        
        if (data.success) {
            const results = data.results;
            let stocks = [];
            
            // 테이블 ID에 따라 적절한 데이터 선택
            if (tableId.includes('oversold')) {
                stocks = results.oversold_stocks || [];
            } else if (tableId.includes('sar')) {
                stocks = results.sar_buy_signals || [];
            } else if (tableId.includes('golden')) {
                stocks = results.golden_cross_stocks || [];
            }
            
            // 시장별 필터링
            if (tableId.includes('kospi')) {
                stocks = stocks.filter(stock => 
                    results.market_results?.KOSPI?.oversold?.includes(stock.ticker) ||
                    results.market_results?.KOSPI?.sar_buy?.includes(stock.ticker) ||
                    results.market_results?.KOSPI?.golden_cross?.includes(stock.ticker)
                );
            } else if (tableId.includes('kosdaq')) {
                stocks = stocks.filter(stock => 
                    results.market_results?.KOSDAQ?.oversold?.includes(stock.ticker) ||
                    results.market_results?.KOSDAQ?.sar_buy?.includes(stock.ticker) ||
                    results.market_results?.KOSDAQ?.golden_cross?.includes(stock.ticker)
                );
            } else if (tableId.includes('konex')) {
                stocks = stocks.filter(stock => 
                    results.market_results?.KONEX?.oversold?.includes(stock.ticker) ||
                    results.market_results?.KONEX?.sar_buy?.includes(stock.ticker) ||
                    results.market_results?.KONEX?.golden_cross?.includes(stock.ticker)
                );
            }
            
            displayAllStocks(tableId, stocks);
        }
    } catch (error) {
        console.error('전체 종목 로드 중 오류:', error);
        // 오류 시 간단한 접기/펼치기로 대체
        toggleSimpleView(tableId);
    }
}

// 전체 종목 표시
function displayAllStocks(tableId, stocks) {
    const tbody = document.getElementById(tableId + '-tbody');
    if (!tbody) return;
    
    // 기존 행 제거 (첫 번째 10개 제외)
    const rows = tbody.querySelectorAll('tr');
    for (let i = 10; i < rows.length; i++) {
        rows[i].remove();
    }
    
    // 나머지 종목들 추가
    for (let i = 10; i < stocks.length; i++) {
        const stock = stocks[i];
        const row = createStockRow(stock, i + 1, tableId);
        tbody.appendChild(row);
    }
}

// 간단한 접기/펼치기 (API 호출 없이)
function toggleSimpleView(tableId) {
    const tbody = document.getElementById(tableId + '-tbody');
    const button = event.target;
    const isExpanded = button.getAttribute('data-expanded') === 'true';
    
    if (!isExpanded) {
        // 모든 행 표시
        const hiddenRows = tbody.querySelectorAll('tr[style*="display: none"]');
        hiddenRows.forEach(row => row.style.display = '');
        
        button.innerHTML = '<i class="fas fa-chevron-up me-1"></i>접기';
        button.setAttribute('data-expanded', 'true');
    } else {
        // 처음 10개만 표시
        showFirstTenStocks(tableId);
    }
}

// 처음 10개 종목만 표시
function showFirstTenStocks(tableId) {
    const tbody = document.getElementById(tableId + '-tbody');
    const button = event.target;
    
    if (!tbody) return;
    
    const rows = tbody.querySelectorAll('tr');
    rows.forEach((row, index) => {
        if (index >= 10) {
            row.style.display = 'none';
        }
    });
    
    // 버튼 텍스트 복원
    const totalCount = rows.length;
    const remainingCount = totalCount - 10;
    button.innerHTML = `<i class="fas fa-chevron-down me-1"></i>더보기 (${remainingCount}개)`;
    button.setAttribute('data-expanded', 'false');
}

// 종목 행 생성
function createStockRow(stock, index, tableId) {
    const row = document.createElement('tr');
    
    // 테이블 타입에 따라 다른 내용 생성
    if (tableId.includes('oversold')) {
        row.innerHTML = `
            <td><span class="badge bg-info">${index}</span></td>
            <td><strong>${stock.name || 'N/A'}</strong></td>
            <td><code>${stock.ticker || 'N/A'}</code></td>
            <td><span class="badge bg-info">${stock.rsi ? stock.rsi.toFixed(2) : '0.00'}</span></td>
            <td><strong>${stock.current_open ? stock.current_open.toLocaleString() : '0'}원</strong></td>
            <td><span class="badge bg-secondary">기타</span></td>
        `;
    } else if (tableId.includes('sar')) {
        row.innerHTML = `
            <td><span class="badge bg-success">${index}</span></td>
            <td><strong>${stock.name || 'N/A'}</strong></td>
            <td><code>${stock.ticker || 'N/A'}</code></td>
            <td><span class="badge bg-info">${stock.rsi ? stock.rsi.toFixed(2) : '0.00'}</span></td>
            <td><span class="badge bg-success">${stock.sar_strength || 'N/A'}</span></td>
            <td><strong>${stock.current_open ? stock.current_open.toLocaleString() : '0'}원</strong></td>
            <td><span class="badge bg-secondary">기타</span></td>
        `;
    } else if (tableId.includes('golden')) {
        const todayBadge = stock.macd_golden_today ? '<span class="badge bg-warning ms-1">오늘 골든크로스</span>' : '';
        row.innerHTML = `
            <td><span class="badge bg-warning">${index}</span></td>
            <td>
                <strong>${stock.name || 'N/A'}</strong>
                ${todayBadge}
            </td>
            <td><code>${stock.ticker || 'N/A'}</code></td>
            <td><span class="badge bg-info">${stock.rsi ? stock.rsi.toFixed(2) : '0.00'}</span></td>
            <td><span class="badge bg-success">${stock.sar_strength || 'N/A'}</span></td>
            <td><span class="badge bg-warning">${stock.macd ? stock.macd.toFixed(2) : '0.00'}</span></td>
            <td><strong>${stock.current_open ? stock.current_open.toLocaleString() : '0'}원</strong></td>
            <td><span class="badge bg-secondary">기타</span></td>
        `;
    }
    
    return row;
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
    document.querySelectorAll('.card, .table').forEach(el => {
        observer.observe(el);
    });
}

// 알림 표시 함수
function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alert-container');
    if (!alertContainer) return;
    
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