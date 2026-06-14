// Login page script
document.addEventListener('DOMContentLoaded', function() {
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
});
