/**
 * Laporan JavaScript
 * Menangani logika laporan dan statistik untuk karyawan/petugas perpustakaan
 */

// Memuat data saat halaman dimuat
document.addEventListener('DOMContentLoaded', function() {
    loadUserInfo();
    
    // Set default dates untuk filter (bulan ini)
    const today = new Date();
    const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);
    
    document.getElementById('tglMulaiPinjam').value = formatDateForInput(firstDay);
    document.getElementById('tglAkhirPinjam').value = formatDateForInput(today);
    document.getElementById('tglMulaiKembali').value = formatDateForInput(firstDay);
    document.getElementById('tglAkhirKembali').value = formatDateForInput(today);
    document.getElementById('statBulan').value = today.getMonth() + 1;
    document.getElementById('statTahun').value = today.getFullYear();
    
    // Setup form handlers
    document.getElementById('filterPeminjamanForm').addEventListener('submit', function(e) {
        e.preventDefault();
        loadLaporanPeminjaman();
    });
    
    document.getElementById('filterPengembalianForm').addEventListener('submit', function(e) {
        e.preventDefault();
        loadLaporanPengembalian();
    });
    
    document.getElementById('filterStatistikForm').addEventListener('submit', function(e) {
        e.preventDefault();
        loadStatistik();
    });
});

// Load user info dari session
function loadUserInfo() {
    fetch('/api/me')
        .then(response => response.json())
        .then(data => {
            if (data.user_id) {
                document.getElementById('userName').textContent = data.nama;
                
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

// Show/hide tabs
function showTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active from all buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(`tab-${tabName}`).classList.add('active');
    
    // Set active button
    event.target.classList.add('active');
}

// Load laporan peminjaman
function loadLaporanPeminjaman() {
    const tglMulai = document.getElementById('tglMulaiPinjam').value;
    const tglAkhir = document.getElementById('tglAkhirPinjam').value;
    
    fetch(`/api/karyawan/laporan/peminjaman?tgl_mulai=${tglMulai}&tgl_akhir=${tglAkhir}`)
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById('laporanPeminjamanBody');
            
            if (!data || data.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" class="text-center">Tidak ada data</td></tr>';
                return;
            }
            
            let html = '';
            data.forEach(laporan => {
                html += `
                    <tr>
                        <td>${laporan.id_pinjam}</td>
                        <td>${laporan.peminjam}</td>
                        <td>${laporan.judul_buku || '-'}</td>
                        <td>${formatDate(laporan.tgl_pinjam)}</td>
                        <td>${formatDate(laporan.tgl_jatuh_tempo)}</td>
                        <td><span class="badge badge-warning">${laporan.status_transaksi}</span></td>
                    </tr>
                `;
            });
            
            tbody.innerHTML = html;
        })
        .catch(error => {
            console.error('Error loading laporan peminjaman:', error);
            showAlert('Gagal memuat laporan peminjaman', 'danger');
        });
}

// Load laporan pengembalian
function loadLaporanPengembalian() {
    const tglMulai = document.getElementById('tglMulaiKembali').value;
    const tglAkhir = document.getElementById('tglAkhirKembali').value;
    
    fetch(`/api/karyawan/laporan/pengembalian?tgl_mulai=${tglMulai}&tgl_akhir=${tglAkhir}`)
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById('laporanPengembalianBody');
            
            if (!data || data.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" class="text-center">Tidak ada data</td></tr>';
                return;
            }
            
            let html = '';
            data.forEach(laporan => {
                html += `
                    <tr>
                        <td>${laporan.id_pinjam}</td>
                        <td>${laporan.peminjam}</td>
                        <td>${formatDate(laporan.tgl_kembali)}</td>
                        <td>Rp ${parseFloat(laporan.denda || 0).toLocaleString('id-ID')}</td>
                        <td>${laporan.petugas_in || '-'}</td>
                    </tr>
                `;
            });
            
            tbody.innerHTML = html;
        })
        .catch(error => {
            console.error('Error loading laporan pengembalian:', error);
            showAlert('Gagal memuat laporan pengembalian', 'danger');
        });
}

// Load statistik bulanan
function loadStatistik() {
    const bulan = document.getElementById('statBulan').value;
    const tahun = document.getElementById('statTahun').value;
    
    fetch(`/api/karyawan/laporan/statistik?bulan=${bulan}&tahun=${tahun}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('statTotalPinjam').textContent = data.total_peminjaman || 0;
            document.getElementById('statTotalKembali').textContent = data.total_pengembalian || 0;
            document.getElementById('statTotalDenda').textContent = 
                `Rp ${parseFloat(data.total_denda || 0).toLocaleString('id-ID')}`;
        })
        .catch(error => {
            console.error('Error loading statistik:', error);
            showAlert('Gagal memuat statistik', 'danger');
        });
}

// Export laporan (placeholder - perlu implementasi backend)
function exportLaporan(tipe) {
    showAlert('Fitur export akan segera tersedia', 'info');
}

// Format tanggal untuk input date (YYYY-MM-DD)
function formatDateForInput(date) {
    const d = new Date(date);
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    const year = d.getFullYear();
    return `${year}-${month}-${day}`;
}

// Format tanggal untuk display (DD/MM/YYYY)
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
