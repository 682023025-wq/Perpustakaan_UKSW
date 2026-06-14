/**
 * Dashboard Karyawan JavaScript
 * Menangani logika dashboard untuk karyawan/petugas perpustakaan
 */

// Memuat data saat halaman dimuat
document.addEventListener('DOMContentLoaded', function() {
    loadUserInfo();
    loadDashboardStats();
    loadCurrentDate();
});

// Load user info dari session
function loadUserInfo() {
    fetch('/api/me')
        .then(response => response.json())
        .then(data => {
            if (data.user_id) {
                document.getElementById('userName').textContent = data.nama;
                document.getElementById('welcomeName').textContent = data.nama;
                
                // Cek role, jika bukan karyawan/admin redirect ke login
                if (data.role !== 'KARYAWAN' && data.role !== 'ADMIN') {
                    window.location.href = '/';
                }
            } else {
                window.location.href = '/';
            }
        })
        .catch(error => {
            console.error('Error loading user info:', error);
            window.location.href = '/';
        });
}

// Load statistik dashboard
function loadDashboardStats() {
    fetch('/api/karyawan/dashboard/stats')
        .then(response => response.json())
        .then(data => {
            document.getElementById('peminjamanAktif').textContent = data.peminjaman_aktif || 0;
            document.getElementById('kembaliHariIni').textContent = data.kembali_hari_ini || 0;
            document.getElementById('dendaBelumLunas').textContent = data.denda_belum_lunas || 0;
            document.getElementById('bukuTersedia').textContent = data.buku_tersedia || 0;
            
            // Load transaksi terbaru
            loadRecentTransactions(data.transaksi_terbaru);
        })
        .catch(error => {
            console.error('Error loading stats:', error);
            showAlert('Gagal memuat statistik dashboard', 'danger');
        });
}

// Load transaksi terbaru ke tabel
function loadRecentTransactions(transactions) {
    const tbody = document.getElementById('recentTransactionsBody');
    
    if (!transactions || transactions.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center">Tidak ada transaksi</td></tr>';
        return;
    }
    
    let html = '';
    transactions.forEach(trx => {
        const statusClass = trx.status === 'Dipinjam' ? 'badge-warning' : 'badge-success';
        html += `
            <tr>
                <td>${trx.id_pinjam}</td>
                <td>${trx.peminjam}</td>
                <td>${formatDate(trx.tgl_pinjam)}</td>
                <td>${formatDate(trx.tgl_kembali_wajib)}</td>
                <td>${trx.petugas_out || '-'}</td>
                <td><span class="badge ${statusClass}">${trx.status}</span></td>
            </tr>
        `;
    });
    
    tbody.innerHTML = html;
}

// Load tanggal saat ini
function loadCurrentDate() {
    const dateElement = document.getElementById('currentDate');
    const options = { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
    };
    const today = new Date();
    dateElement.textContent = today.toLocaleDateString('id-ID', options);
}

// Format tanggal dari YYYY-MM-DD ke DD/MM/YYYY
function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('id-ID');
}

// Logout function
function logout() {
    if (confirm('Apakah Anda yakin ingin logout?')) {
        fetch('/api/logout', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    window.location.href = '/';
                }
            })
            .catch(error => {
                console.error('Error logging out:', error);
            });
    }
}

// Show alert message
function showAlert(message, type = 'info') {
    const alertBox = document.getElementById('alertBox');
    const alertClass = `alert-${type}`;
    
    alertBox.innerHTML = `
        <div class="alert ${alertClass}">
            <span>${message}</span>
        </div>
    `;
    
    setTimeout(() => {
        alertBox.innerHTML = '';
    }, 5000);
}
