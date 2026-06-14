/**
 * Admin Dashboard JavaScript
 * Sistem Informasi Perpustakaan
 */

document.addEventListener('DOMContentLoaded', async function() {
    // Check authentication
    const user = await checkAuth('ADMIN');
    
    if (user) {
        // Update user info in navbar
        document.getElementById('userName').textContent = user.nama;
        document.getElementById('welcomeName').textContent = user.nama;
        
        // Set current date
        const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
        document.getElementById('currentDate').textContent = new Date().toLocaleDateString('id-ID', options);
        
        // Load dashboard statistics
        loadDashboardStats();
    }
});

async function loadDashboardStats() {
    try {
        const stats = await fetchAPI('/admin/dashboard/stats');
        
        // Update stat cards
        document.getElementById('totalUsers').textContent = stats.total_users || 0;
        document.getElementById('totalBuku').textContent = stats.total_buku || 0;
        document.getElementById('peminjamanAktif').textContent = stats.peminjaman_aktif || 0;
        document.getElementById('dendaBelumLunas').textContent = stats.denda_belum_lunas || 0;
        
        // Load recent transactions
        loadRecentTransactions(stats.peminjaman_terbaru || []);
        
    } catch (error) {
        console.error('Error loading stats:', error);
        showAlert('Gagal memuat statistik dashboard', 'error');
    }
}

function loadRecentTransactions(transactions) {
    const tbody = document.getElementById('recentTransactionsBody');
    
    if (!transactions || transactions.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center">Tidak ada data peminjaman terbaru</td></tr>';
        return;
    }
    
    tbody.innerHTML = transactions.map(t => `
        <tr>
            <td>${t.id_pinjam}</td>
            <td>${t.peminjam}</td>
            <td>${t.judul || '-'}</td>
            <td>${formatDate(t.tgl_pinjam)}</td>
            <td>${formatDate(t.tgl_kembali_wajib)}</td>
            <td><span class="badge ${t.status === 'Dipinjam' ? 'badge-warning' : 'badge-success'}">${t.status}</span></td>
        </tr>
    `).join('');
}

async function logout() {
    if (await confirmDialog('Apakah Anda yakin ingin logout?')) {
        await fetchAPI('/logout', { method: 'POST' });
        window.location.href = '/';
    }
}
