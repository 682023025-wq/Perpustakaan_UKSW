// Peminjaman page script
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('peminjaman-form');
    
    // Load peminjaman aktif
    loadPeminjamanAktif();
    
    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const idPeminjam = document.getElementById('id_peminjam').value.trim();
            const idBarcode = document.getElementById('id_barcode').value.trim();
            
            try {
                const result = await apiRequest('/karyawan/peminjaman/api/peminjaman/proses', 'POST', {
                    id_peminjam: idPeminjam,
                    id_barcode: idBarcode
                });
                
                if (result.success) {
                    showAlert(`Peminjaman berhasil! ID: ${result.id_pinjam}`, 'success');
                    form.reset();
                    loadPeminjamanAktif();
                }
            } catch (error) {
                showAlert(error.message, 'error');
            }
        });
    }
});

async function loadPeminjamanAktif() {
    try {
        const data = await apiRequest('/karyawan/peminjaman/api/peminjaman');
        const tbody = document.querySelector('#peminjaman-table tbody');
        
        if (tbody && data.length > 0) {
            tbody.innerHTML = '';
            data.forEach(p => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${p.id_pinjam}</td>
                    <td>${p.nama_peminjam}</td>
                    <td>${p.judul}</td>
                    <td>${formatDate(p.tgl_pinjam)}</td>
                    <td>${formatDate(p.tgl_jatuh_tempo)}</td>
                    <td><span style="color: var(--primary-red); font-weight: bold;">${p.status_transaksi}</span></td>
                `;
                tbody.appendChild(tr);
            });
        } else if (tbody) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align: center;">Tidak ada peminjaman aktif</td></tr>';
        }
    } catch (error) {
        console.error('Error loading peminjaman:', error);
    }
}
