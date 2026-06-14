/**
 * Login Page JavaScript
 * Sistem Informasi Perpustakaan
 */

document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const btnLogin = document.getElementById('btnLogin');
    
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            setLoading(btnLogin, true);
            
            try {
                const response = await fetch('/api/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ username, password })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showAlert('Login berhasil! Mengalihkan...', 'success');
                    setTimeout(() => {
                        window.location.href = data.redirect;
                    }, 1000);
                } else {
                    showAlert(data.message || 'Login gagal. Silakan coba lagi.', 'error');
                    setLoading(btnLogin, false);
                }
            } catch (error) {
                console.error('Login error:', error);
                showAlert('Terjadi kesalahan koneksi. Silakan coba lagi.', 'error');
                setLoading(btnLogin, false);
            }
        });
    }
    
    // Check if already logged in
    checkAlreadyLoggedIn();
});

async function checkAlreadyLoggedIn() {
    try {
        const response = await fetch('/api/me');
        if (response.ok) {
            const user = await response.json();
            if (user.role === 'ADMIN') {
                window.location.href = '/admin/dashboard.html';
            } else {
                window.location.href = '/karyawan/dashboard.html';
            }
        }
    } catch (error) {
        // Not logged in, stay on login page
    }
}
