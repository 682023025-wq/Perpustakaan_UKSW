/**
 * Global JavaScript Utilities
 * Sistem Informasi Perpustakaan
 */

// API Base URL
const API_BASE = '/api';

/**
 * Fetch wrapper dengan error handling
 */
async function fetchAPI(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const config = {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            ...options.headers
        }
    };
    
    try {
        const response = await fetch(url, config);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || 'Terjadi kesalahan');
        }
        
        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

/**
 * Show alert message
 */
function showAlert(message, type = 'info') {
    const alertBox = document.getElementById('alertBox');
    if (!alertBox) return;
    
    const alertClass = {
        'success': 'alert-success',
        'error': 'alert-danger',
        'warning': 'alert-warning',
        'info': 'alert-info'
    }[type] || 'alert-info';
    
    alertBox.innerHTML = `
        <div class="alert ${alertClass}">
            <span>${message}</span>
        </div>
    `;
    
    // Auto hide after 5 seconds
    setTimeout(() => {
        alertBox.innerHTML = '';
    }, 5000);
}

/**
 * Format currency to IDR
 */
function formatCurrency(amount) {
    return new Intl.NumberFormat('id-ID', {
        style: 'currency',
        currency: 'IDR',
        minimumFractionDigits: 0
    }).format(amount);
}

/**
 * Format date to Indonesian locale
 */
function formatDate(dateString) {
    const options = { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
    };
    return new Date(dateString).toLocaleDateString('id-ID', options);
}

/**
 * Get current user from session
 */
async function getCurrentUser() {
    try {
        const user = await fetchAPI('/me');
        return user;
    } catch (error) {
        return null;
    }
}

/**
 * Logout user
 */
async function logout() {
    try {
        await fetchAPI('/logout', { method: 'POST' });
        window.location.href = '/';
    } catch (error) {
        console.error('Logout error:', error);
        window.location.href = '/';
    }
}

/**
 * Check if user is logged in
 */
async function checkAuth(requiredRole = null) {
    const user = await getCurrentUser();
    
    if (!user) {
        window.location.href = '/';
        return null;
    }
    
    if (requiredRole && user.role !== requiredRole) {
        showAlert('Akses ditolak. Anda tidak memiliki izin untuk mengakses halaman ini.', 'error');
        setTimeout(() => {
            window.location.href = requiredRole === 'ADMIN' ? '/admin/dashboard.html' : '/karyawan/dashboard.html';
        }, 2000);
        return null;
    }
    
    return user;
}

/**
 * Loading button state
 */
function setLoading(button, isLoading) {
    if (isLoading) {
        button.disabled = true;
        button.classList.add('loading');
        button.dataset.originalText = button.textContent;
        button.textContent = 'Memproses...';
    } else {
        button.disabled = false;
        button.classList.remove('loading');
        button.textContent = button.dataset.originalText || 'Submit';
    }
}

/**
 * Confirm dialog
 */
function confirmDialog(message) {
    return new Promise((resolve) => {
        if (confirm(message)) {
            resolve(true);
        } else {
            resolve(false);
        }
    });
}

/**
 * Render table rows
 */
function renderTableRows(data, columns, tbodyId) {
    const tbody = document.getElementById(tbodyId);
    if (!tbody) return;
    
    if (!data || data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="' + columns.length + '" class="text-center">Tidak ada data</td></tr>';
        return;
    }
    
    tbody.innerHTML = data.map(item => `
        <tr>
            ${columns.map(col => `<td>${item[col.field] || '-'}</td>`).join('')}
        </tr>
    `).join('');
}

/**
 * Modal functions
 */
function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'flex';
    }
}

function hideModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
    }
}

/**
 * Debounce function for search inputs
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}
