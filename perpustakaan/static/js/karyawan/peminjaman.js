/**
 * Peminjaman Buku JavaScript
 * Menangani logika peminjaman buku untuk karyawan/petugas perpustakaan
 */

// Array untuk menyimpan daftar buku yang akan dipinjam
let daftarBuku = [];
let peminjamData = null;

// Memuat data saat halaman dimuat
document.addEventListener('DOMContentLoaded', function() {
    loadUserInfo();
    loadRiwayatHariIni();
    
    // Setup form submit handler
    document.getElementById('peminjamanForm').addEventListener('submit', function(e) {
        e.preventDefault();
        prosesPeminjaman();
    });
    
    // Enter key untuk barcode
    document.getElementById('barcodeBuku').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            tambahBuku();
        }
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

// Cek informasi peminjam
function cekPeminjam() {
    const idPeminjam = document.getElementById('idPeminjam').value.trim();
    
    if (!idPeminjam) {
        showAlert('Masukkan ID peminjam', 'warning');
        return;
    }
    
    fetch(`/api/admin/users/${idPeminjam}`)
        .then(response => {
            if (response.ok) {
                return response.json();
            }
            throw new Error('Peminjam tidak ditemukan');
        })
        .then(data => {
            peminjamData = data;
            
            // Tampilkan info peminjam
            document.getElementById('infoNama').textContent = data.nama_lengkap || data.nama;
            document.getElementById('infoRole').textContent = data.id_role || data.role;
            document.getElementById('infoStatus').textContent = data.status_aktif || data.status;
            
            // Hitung sisa kuota berdasarkan role
            const maxKuota = getMaxKuota(data.id_role || data.role);
            const kuotaDigunakan = 0; // Akan diupdate dari backend
            
            document.getElementById('infoKuota').textContent = `${maxKuota - kuotaDigunakan} / ${maxKuota}`;
            
            document.getElementById('peminjamInfo').style.display = 'block';
            showAlert('Peminjam ditemukan', 'success');
        })
        .catch(error => {
            showAlert(`Peminjam tidak ditemukan: ${error.message}`, 'danger');
            document.getElementById('peminjamInfo').style.display = 'none';
            peminjamData = null;
        });
}

// Dapatkan kuota maksimal berdasarkan role
function getMaxKuota(role) {
    const kuotaMap = {
        'MHS': 3,
        'DSN': 7,
        'PTGS': 0,
        'SPRADM': 0
    };
    return kuotaMap[role] || 3;
}

// Tambah buku ke daftar
function tambahBuku() {
    const barcode = document.getElementById('barcodeBuku').value.trim();
    
    if (!barcode) {
        showAlert('Masukkan barcode buku', 'warning');
        return;
    }
    
    // Cek apakah sudah ada di daftar
    if (daftarBuku.some(b => b.barcode === barcode)) {
        showAlert('Buku sudah ada di daftar', 'warning');
        return;
    }
    
    // Cek ketersediaan buku (simulasi - perlu API endpoint)
    // Di implementasi nyata, perlu fetch ke API untuk cek status buku
    
    // Tambahkan ke daftar (simulasi)
    daftarBuku.push({
        barcode: barcode,
        judul: 'Memuat...', // Akan diupdate dari API
        status: 'tersedia'
    });
    
    updateDaftarBukuUI();
    document.getElementById('barcodeBuku').value = '';
    showAlert('Buku berhasil ditambahkan', 'success');
}

// Update UI daftar buku
function updateDaftarBukuUI() {
    const tbody = document.getElementById('daftarBukuBody');
    
    if (daftarBuku.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center">Belum ada buku</td></tr>';
        return;
    }
    
    let html = '';
    daftarBuku.forEach((buku, index) => {
        html += `
            <tr>
                <td>${index + 1}</td>
                <td>${buku.barcode}</td>
                <td>${buku.judul}</td>
                <td><span class="badge badge-tersedia">${buku.status}</span></td>
                <td>
                    <button type="button" class="btn-delete" onclick="hapusBuku(${index})">
                        🗑️ Hapus
                    </button>
                </td>
            </tr>
        `;
    });
    
    tbody.innerHTML = html;
}

// Hapus buku dari daftar
function hapusBuku(index) {
    daftarBuku.splice(index, 1);
    updateDaftarBukuUI();
}

// Proses peminjaman
function prosesPeminjaman() {
    if (!peminjamData) {
        showAlert('Silakan cek data peminjam terlebih dahulu', 'warning');
        return;
    }
    
    if (daftarBuku.length === 0) {
        showAlert('Tambahkan minimal 1 buku', 'warning');
        return;
    }
    
    const payload = {
        id_peminjam: peminjamData.id_user || peminjamData.id,
        barcode_list: daftarBuku.map(b => b.barcode)
    };
    
    fetch('/api/karyawan/peminjaman', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert(`Peminjaman berhasil! ID Pinjam: ${data.id_pinjam}`, 'success');
            
            // Reset form
            daftarBuku = [];
            updateDaftarBukuUI();
            document.getElementById('peminjamanForm').reset();
            document.getElementById('peminjamInfo').style.display = 'none';
            peminjamData = null;
            
            // Reload riwayat
            loadRiwayatHariIni();
        } else {
            showAlert(data.message || 'Gagal memproses peminjaman', 'danger');
        }
    })
    .catch(error => {
        showAlert('Terjadi kesalahan saat memproses peminjaman', 'danger');
        console.error('Error:', error);
    });
}

// Load riwayat peminjaman hari ini
function loadRiwayatHariIni() {
    fetch('/api/karyawan/peminjaman/riwayat?status=Dipinjam')
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById('riwayatHariIniBody');
            
            if (!data || data.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" class="text-center">Tidak ada peminjaman hari ini</td></tr>';
                return;
            }
            
            let html = '';
            data.forEach(trx => {
                html += `
                    <tr>
                        <td>${trx.id_pinjam}</td>
                        <td>${trx.peminjam}</td>
                        <td>${trx.jumlah_buku || '-'}</td>
                        <td>${formatDate(trx.tgl_pinjam)}</td>
                        <td>${formatDate(trx.tgl_jatuh_tempo)}</td>
                        <td><span class="badge badge-warning">${trx.status}</span></td>
                    </tr>
                `;
            });
            
            tbody.innerHTML = html;
        })
        .catch(error => {
            console.error('Error loading riwayat:', error);
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
