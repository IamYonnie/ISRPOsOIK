// MIT License

/**
 * Main JavaScript file for Version Tracker application
 */

// API Base URL
const API_BASE = '/api';

/**
 * Fetch with error handling
 */
async function apiFetch(url, options = {}) {
    const response = await fetch(url, options);
    if (!response.ok) {
        throw new Error(`API Error: ${response.status}`);
    }
    return response.json();
}

/**
 * Format date to locale string
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
 * Format datetime to locale string
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
 * Show notification toast
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
 * Load and display notifications
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
        
        // Show tooltip with notifications
        if (notifBell && data.notifications && data.notifications.length > 0) {
            const notifText = data.notifications
                .map(n => `${n.project}: ${n.old_version} → ${n.new_version}`)
                .join('\n');
            notifBell.title = notifText;
            
            // Add click handler to show notifications
            notifBell.style.cursor = 'pointer';
            notifBell.onclick = function(e) {
                e.preventDefault();
                showNotificationsModal(data.notifications);
            };
        }
    } catch (error) {
        console.error('Error loading notifications:', error);
    }
}

/**
 * Show notifications in modal
 */
function showNotificationsModal(notifications) {
    let html = '<div class="list-group">';
    
    if (notifications.length === 0) {
        html += '<p class="text-muted p-3">Нет новых уведомлений</p>';
    } else {
        notifications.forEach(notif => {
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
                        <span class="badge bg-info ms-2">${notif.update_type}</span>
                    </p>
                </div>
            `;
        });
    }
    
    html += '</div>';
    
    // Create modal
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
    
    // Remove old modal if exists
    const oldModal = document.getElementById('notificationsModal');
    if (oldModal) oldModal.remove();
    
    // Add new modal
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('notificationsModal'));
    modal.show();
}

/**
 * Check API health
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
 * Initialize application
 */
document.addEventListener('DOMContentLoaded', function() {
    // Load notifications immediately
    loadNotifications();
    
    // Refresh notifications every 10 seconds
    setInterval(loadNotifications, 10000);
    
    // Check health
    checkHealth();
});

/**
 * Export functions for global use
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
