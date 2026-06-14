/**
 * Denda JavaScript
 * Menangani logika manajemen denda untuk karyawan/petugas perpustakaan
 */

// Memuat data saat halaman dimuat
document.addEventListener('DOMContentLoaded', function() {
    loadUserInfo();
    loadDendaList();
    
    // Setup filter form
    document.getElementById('filterForm').addEventListener('submit', function(e) {
        e.preventDefault();
        loadDendaList();
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

// Load daftar denda
function loadDendaList() {
    const status = document.getElementById('filterStatus').value;
    const search = document.getElementById('searchDenda').value;
    
    let url = '/api/karyawan/denda';
    const params = new URLSearchParams();
    
    if (status) {
        params.append('status', status);
    }
    
    if (search) {
        params.append('search', search);
    }
    
    if (params.toString()) {
        url += '?' + params.toString();
    }
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById('dendaTableBody');
            
            if (!data || data.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7" class="text-center">Tidak ada data denda</td></tr>';
                return;
            }
            
            let html = '';
            let totalBelumLunas = 0;
            let totalLunas = 0;
            let nominalBelumLunas = 0;
            
            data.forEach(denda => {
                const statusClass = denda.status_bayar === 'Lunas' ? 'badge-lunas' : 'badge-belum-lunas';
                const btnBayar = denda.status_bayar === 'Belum Lunas' 
                    ? `<button class="btn-bayar" onclick="bayarDenda('${denda.id_denda}')">💵 Bayar</button>`
                    : '<span class="text-muted">-</span>';
                
                if (denda.status_bayar === 'Lunas') {
                    totalLunas++;
                } else {
                    totalBelumLunas++;
                    nominalBelumLunas += parseFloat(denda.nominal_denda || 0);
                }
                
                html += `
                    <tr>
                        <td>${denda.id_denda}</td>
                        <td>${denda.id_pinjam}</td>
                        <td>${denda.peminjam || '-'}</td>
                        <td>Rp ${parseFloat(denda.nominal_denda || 0).toLocaleString('id-ID')}</td>
                        <td><span class="badge ${statusClass}">${denda.status_bayar}</span></td>
                        <td>${formatDate(denda.tgl_bayar)}</td>
                        <td>${btnBayar}</td>
                    </tr>
                `;
            });
            
            tbody.innerHTML = html;
            
            // Update statistik
            document.getElementById('totalBelumLunas').textContent = totalBelumLunas;
            document.getElementById('totalLunas').textContent = totalLunas;
            document.getElementById('totalNominalBelumLunas').textContent = 
                `Rp ${nominalBelumLunas.toLocaleString('id-ID')}`;
        })
        .catch(error => {
            console.error('Error loading denda:', error);
            showAlert('Gagal memuat data denda', 'danger');
        });
}

// Bayar denda
function bayarDenda(idDenda) {
    if (!confirm('Apakah Anda yakin ingin menandai denda ini sebagai lunas?')) {
        return;
    }
    
    fetch(`/api/karyawan/denda/${idDenda}/bayar`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('Pembayaran denda berhasil dicatat', 'success');
            loadDendaList();
        } else {
            showAlert(data.message || 'Gagal memproses pembayaran', 'danger');
        }
    })
    .catch(error => {
        showAlert('Terjadi kesalahan saat memproses pembayaran', 'danger');
        console.error('Error:', error);
    });
}

// Format tanggal
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
