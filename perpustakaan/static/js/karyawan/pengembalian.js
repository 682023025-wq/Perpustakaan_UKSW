/**
 * Pengembalian Buku JavaScript
 * Menangani logika pengembalian buku untuk karyawan/petugas perpustakaan
 */

let peminjamanData = null;

// Memuat data saat halaman dimuat
document.addEventListener('DOMContentLoaded', function() {
    loadUserInfo();
    loadRiwayatPengembalian();
    
    // Setup form submit handler
    document.getElementById('pengembalianForm').addEventListener('submit', function(e) {
        e.preventDefault();
        prosesPengembalian();
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

// Cek peminjaman berdasarkan ID
function cekPeminjaman() {
    const idPinjam = document.getElementById('idPinjam').value.trim();
    
    if (!idPinjam) {
        showAlert('Masukkan ID peminjaman', 'warning');
        return;
    }
    
    // Fetch detail peminjaman dari API
    fetch(`/api/karyawan/peminjaman/${idPinjam}`)
        .then(response => {
            if (response.ok) {
                return response.json();
            }
            throw new Error('Peminjaman tidak ditemukan');
        })
        .then(data => {
            peminjamanData = data;
            
            // Tampilkan info peminjaman
            document.getElementById('infoIdPinjam').textContent = data.id_pinjam;
            document.getElementById('infoPeminjam').textContent = data.peminjam;
            document.getElementById('infoTglPinjam').textContent = formatDate(data.tgl_pinjam);
            document.getElementById('infoJatuhTempo').textContent = formatDate(data.tgl_jatuh_tempo);
            document.getElementById('infoStatus').textContent = data.status_transaksi;
            
            // Tampilkan daftar buku
            const tbody = document.getElementById('daftarBukuPengembalian');
            if (data.buku && data.buku.length > 0) {
                let html = '';
                data.buku.forEach(buku => {
                    html += `
                        <tr>
                            <td>${buku.barcode || buku.id_barcode}</td>
                            <td>${buku.judul}</td>
                        </tr>
                    `;
                });
                tbody.innerHTML = html;
            } else {
                tbody.innerHTML = '<tr><td colspan="2" class="text-center">Tidak ada buku</td></tr>';
            }
            
            // Cek apakah terlambat
            const today = new Date();
            const jatuhTempo = new Date(data.tgl_jatuh_tempo);
            
            if (today > jatuhTempo) {
                const hariTerlambat = Math.floor((today - jatuhTempo) / (1000 * 60 * 60 * 24));
                const denda = hariTerlambat * 1000; // Rp 1000 per hari
                
                document.getElementById('dendaDetail').textContent = 
                    `Terlambat ${hariTerlambat} hari. Denda: Rp ${denda.toLocaleString('id-ID')}`;
                document.getElementById('dendaInfo').style.display = 'block';
            } else {
                document.getElementById('dendaInfo').style.display = 'none';
            }
            
            document.getElementById('peminjamanInfo').style.display = 'block';
            showAlert('Peminjaman ditemukan', 'success');
        })
        .catch(error => {
            showAlert(`Peminjaman tidak ditemukan: ${error.message}`, 'danger');
            document.getElementById('peminjamanInfo').style.display = 'none';
            peminjamanData = null;
        });
}

// Proses pengembalian
function prosesPengembalian() {
    if (!peminjamanData) {
        showAlert('Silakan cek data peminjaman terlebih dahulu', 'warning');
        return;
    }
    
    if (peminjamanData.status_transaksi !== 'Dipinjam') {
        showAlert('Peminjaman ini sudah dikembalikan', 'warning');
        return;
    }
    
    const payload = {
        id_pinjam: peminjamanData.id_pinjam
    };
    
    fetch('/api/karyawan/pengembalian', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            let message = 'Pengembalian berhasil diproses!';
            
            if (data.denda && data.denda > 0) {
                message += ` Terdapat denda: Rp ${data.denda.toLocaleString('id-ID')}`;
                showAlert(message, 'warning');
            } else {
                showAlert(message, 'success');
            }
            
            // Reset form
            document.getElementById('pengembalianForm').reset();
            document.getElementById('peminjamanInfo').style.display = 'none';
            peminjamanData = null;
            
            // Reload riwayat
            loadRiwayatPengembalian();
        } else {
            showAlert(data.message || 'Gagal memproses pengembalian', 'danger');
        }
    })
    .catch(error => {
        showAlert('Terjadi kesalahan saat memproses pengembalian', 'danger');
        console.error('Error:', error);
    });
}

// Load riwayat pengembalian hari ini
function loadRiwayatPengembalian() {
    // Ini perlu endpoint baru di backend untuk riwayat pengembalian
    // Untuk sementara, tampilkan placeholder
    const tbody = document.getElementById('riwayatPengembalianBody');
    tbody.innerHTML = '<tr><td colspan="5" class="text-center">Belum ada pengembalian hari ini</td></tr>';
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
