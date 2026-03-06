// MIT License

/**
 * Основной JavaScript файл для приложения Version Tracker
 */

// Базовый URL API
const API_BASE = '/api';

/**
 * Fetch с обработкой ошибок
 */
async function apiFetch(url, options = {}) {
    const response = await fetch(url, options);
    if (!response.ok) {
        throw new Error(`API Error: ${response.status}`);
    }
    return response.json();
}

/**
 * Форматировать дату в локальную строку
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

/**
 * Форматировать дату и время в локальную строку
 */
function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('ru-RU', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Показать уведомление (toast)
 */
function showNotification(message, type = 'info') {
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert" style="position: fixed; top: 20px; right: 20px; z-index: 1000; min-width: 300px;">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    document.body.insertAdjacentHTML('beforeend', alertHtml);
    
    setTimeout(() => {
        const alert = document.querySelector('.alert');
        if (alert) alert.remove();
    }, 5000);
}

/**
 * Загрузить и отобразить уведомления
 */
async function loadNotifications() {
    try {
        const data = await apiFetch(`${API_BASE}/notifications/unread`);
        const notifBell = document.getElementById('notifBell');
        const notifCount = document.getElementById('notifCount');
        
        if (data.count > 0) {
            notifCount.textContent = data.count;
            notifCount.style.display = 'inline-block';
        } else {
            notifCount.style.display = 'none';
        }
        
        // Установить обработчик клика для значка
        if (notifBell) {
            notifBell.style.cursor = 'pointer';
            notifBell.onclick = function(e) {
                e.preventDefault();
                showNotificationsModal(data.notifications || []);
            };
        }
    } catch (error) {
        console.error('Error loading notifications:', error);
    }
}

/**
 * Показать уведомления в модальном окне
 */
function showNotificationsModal(notifications) {
    let html = '<div class="list-group">';
    let projectNames = new Set();
    
    if (notifications.length === 0) {
        html += '<p class="text-muted p-3">Нет новых уведомлений</p>';
    } else {
        notifications.forEach(notif => {
            projectNames.add(notif.project);
            const date = new Date(notif.detected_at).toLocaleString('ru-RU');
            html += `
                <div class="list-group-item">
                    <div class="d-flex w-100 justify-content-between">
                        <h6 class="mb-1">${notif.project}</h6>
                        <small class="text-muted">${date}</small>
                    </div>
                    <p class="mb-1">
                        <code>${notif.old_version}</code> → 
                        <code class="text-success">${notif.new_version}</code>
                        <span class="badge bg-info ms-2">${notif.update_type || 'update'}</span>
                    </p>
                </div>
            `;
        });
    }
    
    html += '</div>';
    
    // Создать модальное окно
    const modalHtml = `
        <div class="modal fade" id="notificationsModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Уведомления об обновлениях</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        ${html}
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Закрыть</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Удалить старое модальное окно, если оно существует
    const oldModal = document.getElementById('notificationsModal');
    if (oldModal) oldModal.remove();
    
    // Добавить новое модальное окно
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Показать модальное окно
    const modal = new bootstrap.Modal(document.getElementById('notificationsModal'));
    
    // Отметить уведомления как прочитанные при закрытии модального окна
    document.getElementById('notificationsModal').addEventListener('hidden.bs.modal', function() {
        // Отметить уведомления каждого проекта как прочитанные
        projectNames.forEach(projectName => {
            fetch(`/api/notifications/mark-read/${encodeURIComponent(projectName)}`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'}
            })
            .then(response => response.json())
            .catch(error => console.error('Error marking notifications as read:', error));
        });
        
        // Перезагрузить уведомления, чтобы обновить значок
        loadNotifications();
    });
    
    modal.show();
}

/**
 * Проверить здоровье API
 */
async function checkHealth() {
    try {
        const response = await fetch('/health');
        return response.ok;
    } catch (error) {
        console.error('Health check failed:', error);
        return false;
    }
}

/**
 * Инициализировать приложение
 */
document.addEventListener('DOMContentLoaded', function() {
    // Загрузить уведомления сразу же
    loadNotifications();
    
    // Обновлять уведомления каждые 10 секунд
    setInterval(loadNotifications, 10000);
    
    // Проверить здоровье API
    checkHealth();
});

/**
 * Экспортировать функции для глобального использования
 */
window.VersionTracker = {
    apiFetch,
    formatDate,
    formatDateTime,
    showNotification,
    loadNotifications,
    showNotificationsModal,
    checkHealth
};
