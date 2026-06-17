document.addEventListener('DOMContentLoaded', function() {
    // 1. Logic Toggle Password Visibility
    const togglePasswordBtn = document.getElementById('togglePassword');
    const passwordInput = document.getElementById('password');
    const eyeOpen = togglePasswordBtn.querySelector('.eye-open');
    const eyeClosed = togglePasswordBtn.querySelector('.eye-closed');

    if (togglePasswordBtn && passwordInput) {
        togglePasswordBtn.addEventListener('click', function() {
            // Cek tipe input saat ini
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            
            // Toggle icon visibility
            if (type === 'text') {
                eyeOpen.style.display = 'none';
                eyeClosed.style.display = 'block';
            } else {
                eyeOpen.style.display = 'block';
                eyeClosed.style.display = 'none';
            }
        });
    }

    // 2. Logic Lupa Password
    const forgotPasswordLink = document.getElementById('forgotPasswordLink');
    if (forgotPasswordLink) {
        forgotPasswordLink.addEventListener('click', function(e) {
            e.preventDefault(); // Mencegah link pindah halaman
            showAlert('Silahkan hubungi admin untuk reset password.', 'warning');
        });
    }

    // 3. Logic Submit Form Validation
    const form = document.querySelector('.login-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            const username = document.getElementById('username').value.trim();
            const password = document.getElementById('password').value;
            
            if (!username || !password) {
                e.preventDefault();
                showAlert('Username dan password harus diisi', 'error');
            }
        });
    }

    // Helper Function untuk Menampilkan Alert
    function showAlert(message, type = 'error') {
        const container = document.getElementById('dynamic-alert-container');
        
        // Hapus alert lama jika ada
        container.innerHTML = '';

        const alertDiv = document.createElement('div');
        alertDiv.className = `error-message ${type === 'warning' ? 'alert-warning' : ''}`;
        
        // Styling inline sederhana untuk warning agar beda warna (opsional, bisa pakai class CSS)
        if (type === 'warning') {
            alertDiv.style.backgroundColor = '#fff3e0';
            alertDiv.style.color = '#ef6c00';
            alertDiv.style.borderLeftColor = '#ef6c00';
        }

        alertDiv.textContent = message;
        container.appendChild(alertDiv);

        // Auto hide setelah 5 detik
        setTimeout(() => {
            alertDiv.style.opacity = '0';
            setTimeout(() => alertDiv.remove(), 300);
        }, 5000);
    }
});