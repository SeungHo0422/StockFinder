// StockFinder Settings JavaScript

// 페이지 로딩 시 실행
document.addEventListener('DOMContentLoaded', function() {
    loadSettings();
    loadSystemInfo();
    setupEventListeners();
});

// 설정 로드 함수
function loadSettings() {
    try {
        // 로컬 스토리지에서 설정 불러오기
        const settings = JSON.parse(localStorage.getItem('stockfinderSettings') || '{}');
        
        // 텔레그램 설정
        if (settings.telegram) {
            document.getElementById('telegram-token').value = settings.telegram.token || '';
            document.getElementById('telegram-chat-id').value = settings.telegram.chatId || '';
            document.getElementById('telegram-enabled').checked = settings.telegram.enabled || false;
        }
        
        // 스케줄러 설정
        if (settings.scheduler) {
            document.getElementById('scheduler-time').value = settings.scheduler.time || '09:30';
            document.getElementById('scheduler-rsi').value = settings.scheduler.rsi || '30';
            document.getElementById('scheduler-market').value = settings.scheduler.market || 'ALL';
            document.getElementById('scheduler-enabled').checked = settings.scheduler.enabled || false;
        }
        
        console.log('설정을 불러왔습니다.');
    } catch (error) {
        console.error('설정 로드 중 오류:', error);
        showAlert('설정을 불러오는 중 오류가 발생했습니다.', 'warning');
    }
}

// 시스템 정보 로드
async function loadSystemInfo() {
    try {
        // 시장 통계 API 호출
        const response = await fetch('/api/market-stats');
        if (response.ok) {
            const data = await response.json();
            if (data.ALL) {
                document.getElementById('total-stocks').textContent = data.ALL.count.toLocaleString();
            }
        }
        
        // 최근 업데이트 정보
        const statusResponse = await fetch('/api/screening-status');
        if (statusResponse.ok) {
            const statusData = await statusResponse.json();
            if (statusData.has_results && statusData.last_update) {
                document.getElementById('last-update').textContent = formatDate(statusData.last_update);
            } else {
                document.getElementById('last-update').textContent = '없음';
            }
        }
    } catch (error) {
        console.error('시스템 정보 로드 오류:', error);
        document.getElementById('total-stocks').textContent = '오류';
        document.getElementById('last-update').textContent = '오류';
    }
}

// 이벤트 리스너 설정
function setupEventListeners() {
    // 텔레그램 토큰 표시/숨기기
    const tokenInput = document.getElementById('telegram-token');
    tokenInput.addEventListener('dblclick', function() {
        this.type = this.type === 'password' ? 'text' : 'password';
    });
    
    // 폼 변경 시 자동 저장 알림
    const formInputs = document.querySelectorAll('input, select');
    formInputs.forEach(input => {
        input.addEventListener('change', function() {
            showAlert('설정이 변경되었습니다. 저장을 잊지 마세요.', 'info', 3000);
        });
    });
}

// 텔레그램 연결 테스트
async function testTelegram() {
    const token = document.getElementById('telegram-token').value.trim();
    const chatId = document.getElementById('telegram-chat-id').value.trim();
    
    if (!token || !chatId) {
        showAlert('텔레그램 봇 토큰과 채팅 ID를 모두 입력해주세요.', 'warning');
        return;
    }
    
    showAlert('텔레그램 연결을 테스트하는 중...', 'info');
    
    try {
        const response = await fetch('/api/test-telegram', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                token: token,
                chat_id: chatId
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert('텔레그램 연결 테스트가 성공했습니다! 📱', 'success');
        } else {
            showAlert(`텔레그램 연결 실패: ${result.message}`, 'danger');
        }
    } catch (error) {
        console.error('텔레그램 테스트 오류:', error);
        showAlert('텔레그램 연결 테스트 중 오류가 발생했습니다.', 'danger');
    }
}

// 스케줄러 시작
async function startScheduler() {
    const enabled = document.getElementById('scheduler-enabled').checked;
    
    if (!enabled) {
        showAlert('스케줄러를 먼저 활성화해주세요.', 'warning');
        return;
    }
    
    const settings = {
        time: document.getElementById('scheduler-time').value,
        rsi: document.getElementById('scheduler-rsi').value,
        market: document.getElementById('scheduler-market').value,
        enabled: enabled
    };
    
    showAlert('스케줄러를 시작하는 중...', 'info');
    
    try {
        const response = await fetch('/api/start-scheduler', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(settings)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert('스케줄러가 시작되었습니다! ⏰', 'success');
        } else {
            showAlert(`스케줄러 시작 실패: ${result.message}`, 'danger');
        }
    } catch (error) {
        console.error('스케줄러 시작 오류:', error);
        showAlert('스케줄러 시작 중 오류가 발생했습니다.', 'danger');
    }
}

// 시장 데이터 새로고침
async function refreshMarketData() {
    showAlert('시장 데이터를 새로고침하는 중...', 'info');
    
    try {
        const response = await fetch('/api/refresh-market-data', {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert('시장 데이터가 새로고침되었습니다! 📈', 'success');
            loadSystemInfo(); // 시스템 정보 다시 로드
        } else {
            showAlert(`시장 데이터 새로고침 실패: ${result.message}`, 'danger');
        }
    } catch (error) {
        console.error('시장 데이터 새로고침 오류:', error);
        showAlert('시장 데이터 새로고침 중 오류가 발생했습니다.', 'danger');
    }
}

// 오래된 결과 정리
async function clearOldResults() {
    if (!confirm('오래된 스크리닝 결과를 정리하시겠습니까?')) {
        return;
    }
    
    showAlert('오래된 결과를 정리하는 중...', 'info');
    
    try {
        const response = await fetch('/api/clear-old-results', {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(`${result.deleted_count}개의 오래된 결과가 정리되었습니다! 🗑️`, 'success');
        } else {
            showAlert(`결과 정리 실패: ${result.message}`, 'danger');
        }
    } catch (error) {
        console.error('결과 정리 오류:', error);
        showAlert('결과 정리 중 오류가 발생했습니다.', 'danger');
    }
}

// 결과 내보내기
async function exportResults() {
    showAlert('결과를 내보내는 중...', 'info');
    
    try {
        const response = await fetch('/api/export-results');
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = `stockfinder_results_${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            showAlert('결과가 성공적으로 내보내졌습니다! 💾', 'success');
        } else {
            const result = await response.json();
            showAlert(`결과 내보내기 실패: ${result.message}`, 'danger');
        }
    } catch (error) {
        console.error('결과 내보내기 오류:', error);
        showAlert('결과 내보내기 중 오류가 발생했습니다.', 'danger');
    }
}

// 설정 저장
function saveSettings() {
    try {
        const settings = {
            telegram: {
                token: document.getElementById('telegram-token').value.trim(),
                chatId: document.getElementById('telegram-chat-id').value.trim(),
                enabled: document.getElementById('telegram-enabled').checked
            },
            scheduler: {
                time: document.getElementById('scheduler-time').value,
                rsi: document.getElementById('scheduler-rsi').value,
                market: document.getElementById('scheduler-market').value,
                enabled: document.getElementById('scheduler-enabled').checked
            },
            savedAt: new Date().toISOString()
        };
        
        localStorage.setItem('stockfinderSettings', JSON.stringify(settings));
        showAlert('설정이 저장되었습니다! ✅', 'success');
        
        console.log('설정 저장 완료:', settings);
    } catch (error) {
        console.error('설정 저장 오류:', error);
        showAlert('설정 저장 중 오류가 발생했습니다.', 'danger');
    }
}

// 알림 표시 함수
function showAlert(message, type = 'info', duration = 5000) {
    const alertContainer = document.getElementById('alert-container');
    const alertId = 'alert-' + Date.now();
    
    const alertHTML = `
        <div id="${alertId}" class="alert alert-${type} alert-dismissible fade show mb-2" role="alert">
            <div class="d-flex align-items-center">
                <i class="fas fa-${getAlertIcon(type)} me-2"></i>
                <span>${message}</span>
            </div>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    alertContainer.insertAdjacentHTML('beforeend', alertHTML);
    
    // 자동으로 알림 제거
    if (duration > 0) {
        setTimeout(() => {
            const alert = document.getElementById(alertId);
            if (alert) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, duration);
    }
}

// 알림 타입에 따른 아이콘 반환
function getAlertIcon(type) {
    const icons = {
        'success': 'check-circle',
        'danger': 'exclamation-triangle',
        'warning': 'exclamation-circle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// 날짜 포맷팅 함수
function formatDate(dateString) {
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('ko-KR') + ' ' + date.toLocaleTimeString('ko-KR', {
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch (error) {
        return dateString;
    }
}

// 브라우저 호환성 체크
function checkBrowserCompatibility() {
    if (!window.localStorage) {
        showAlert('이 브라우저는 로컬 스토리지를 지원하지 않습니다. 설정이 저장되지 않을 수 있습니다.', 'warning');
    }
    
    if (!window.fetch) {
        showAlert('이 브라우저는 최신 웹 기술을 지원하지 않습니다. 일부 기능이 제한될 수 있습니다.', 'warning');
    }
}

// 페이지 언로드 시 경고
window.addEventListener('beforeunload', function(e) {
    const currentSettings = JSON.stringify({
        telegram: {
            token: document.getElementById('telegram-token').value.trim(),
            chatId: document.getElementById('telegram-chat-id').value.trim(),
            enabled: document.getElementById('telegram-enabled').checked
        },
        scheduler: {
            time: document.getElementById('scheduler-time').value,
            rsi: document.getElementById('scheduler-rsi').value,
            market: document.getElementById('scheduler-market').value,
            enabled: document.getElementById('scheduler-enabled').checked
        }
    });
    
    const savedSettings = localStorage.getItem('stockfinderSettings') || '{}';
    
    if (currentSettings !== savedSettings) {
        e.preventDefault();
        e.returnValue = '저장하지 않은 변경사항이 있습니다. 페이지를 떠나시겠습니까?';
    }
});

// 브라우저 호환성 체크 실행
checkBrowserCompatibility(); 