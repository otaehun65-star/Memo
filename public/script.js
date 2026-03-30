document.addEventListener('DOMContentLoaded', () => {
    const memoInput = document.getElementById('memoInput');
    const charCount = document.getElementById('charCount');

    // Character countdown
    const maxLength = 150;
    memoInput.addEventListener('input', () => {
        const length = memoInput.value.length;
        if (length > maxLength) {
            memoInput.value = memoInput.value.substring(0, maxLength);
        }
        charCount.textContent = `${memoInput.value.length}/${maxLength}`;
        
        if (memoInput.value.length === maxLength) {
            charCount.style.color = 'var(--danger)';
        } else {
            charCount.style.color = 'var(--text-hint)';
        }
    });

    // Auto load on start
    loadMemo('view', true);
});

const API_URL = '/api/memo';
let toastTimeout;
let currentMode = 'view'; // 'view' or 'delete'

function showToast(message, isError = false) {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toastMessage');
    
    toastMessage.textContent = message;
    toast.style.background = isError ? 'var(--danger)' : '#1F2937';
    toast.classList.add('show');
    
    clearTimeout(toastTimeout);
    toastTimeout = setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

function formatDate(dateStr) {
    const d = new Date(dateStr);
    return `${d.getFullYear()}.${String(d.getMonth()+1).padStart(2,'0')}.${String(d.getDate()).padStart(2,'0')} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`;
}

async function saveMemo() {
    const memoInput = document.getElementById('memoInput');
    const charCount = document.getElementById('charCount');
    const content = memoInput.value.trim();
    const btn = document.getElementById('btnSave');
    
    if (!content) {
        showToast('메모를 입력해주세요.', true);
        memoInput.focus();
        return;
    }

    // Button loading state
    const originalText = btn.innerHTML;
    btn.innerHTML = '저장중...';
    btn.style.opacity = '0.7';

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ content })
        });

        if (response.ok) {
            showToast('✅ 성공적으로 저장되었습니다.');
            memoInput.value = '';
            charCount.textContent = '0/150';
            // Refresh list
            loadMemo(currentMode, true);
        } else {
            throw new Error('Save failed');
        }
    } catch (error) {
        showToast('❌ 저장에 실패했습니다.', true);
        console.error(error);
    } finally {
        btn.innerHTML = originalText;
        btn.style.opacity = '1';
    }
}

async function loadMemo(mode = 'view', silent = false) {
    currentMode = mode;
    const btnId = mode === 'view' ? 'btnLoad' : 'btnDelete';
    const btn = document.getElementById(btnId);
    const memoListWrapper = document.getElementById('memoListWrapper');
    const memoList = document.getElementById('memoList');
    const listTitle = document.getElementById('listTitle');

    if (!silent) {
        btn.innerHTML = '로딩중...';
        btn.style.opacity = '0.7';
    }

    listTitle.textContent = mode === 'view' ? '저장된 메모' : '삭제할 메모 선택';

    try {
        const response = await fetch(API_URL);
        const result = await response.json();
        
        if (response.ok && result.data) {
            memoList.innerHTML = '';
            
            if (result.data.length === 0) {
                memoList.innerHTML = '<div style="text-align:center; padding: 20px; color: var(--text-hint); font-size:14px;">저장된 메모가 없습니다.</div>';
            } else {
                result.data.forEach(memo => {
                    const div = document.createElement('div');
                    div.className = `memo-item ${mode === 'delete' ? 'delete-mode' : ''}`;
                    if (mode === 'delete') {
                        div.onclick = () => confirmDeleteMemo(memo.id);
                    }
                    
                    div.innerHTML = `
                        <div style="flex:1">
                            <div class="memo-content">${memo.content}</div>
                            <div class="memo-date">${formatDate(memo.timestamp)}</div>
                        </div>
                        ${mode === 'delete' ? '<div class="delete-icon">✖</div>' : ''}
                    `;
                    memoList.appendChild(div);
                });
            }
            
            memoListWrapper.classList.remove('hidden');
            if (!silent) showToast(mode === 'view' ? '🔄 메모를 불러왔습니다.' : '🗑️ 삭제할 메모를 선택하세요.');
        }
    } catch (error) {
        if (!silent) showToast('❌ 불러오기에 실패했습니다.', true);
        console.error(error);
    } finally {
        if (!silent) {
            btn.innerHTML = mode === 'view' ? '<span class="btn-text">불러오기</span>' : '<span class="btn-text">삭제</span>';
            btn.style.opacity = '1';
        }
    }
}

async function confirmDeleteMemo(id) {
    try {
        const response = await fetch(`${API_URL}/${id}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            showToast('🗑️ 삭제되었습니다.');
            loadMemo('delete', true);
        } else {
            throw new Error('Delete failed');
        }
    } catch (error) {
        showToast('❌ 삭제에 실패했습니다.', true);
        console.error(error);
    }
}
