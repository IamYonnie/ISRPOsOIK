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
        if (notifBell && data.notifications.length > 0) {
            const notifText = data.notifications
                .map(n => `${n.project}: ${n.old_version} → ${n.new_version}`)
                .join('\n');
            notifBell.title = notifText;
        }
    } catch (error) {
        console.error('Error loading notifications:', error);
    }
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
    // Load notifications
    loadNotifications();
    
    // Refresh notifications every 30 seconds
    setInterval(loadNotifications, 30000);
    
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
    checkHealth
};
