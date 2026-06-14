// Laporan JavaScript
let allLaporan = [];

document.addEventListener('DOMContentLoaded', function() {
    loadLaporan();
});

function loadLaporan() {
    fetch('/api/karyawan/laporan')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                allLaporan = data.laporan;
                renderLaporan(allLaporan);
            }
        })
        .catch(error => console.error('Error loading laporan:', error));
}

function renderLaporan(laporanList) {
    const tbody = document.querySelector('#laporan-table tbody');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    laporanList.forEach(item => {
        const tr = document.createElement('tr');
        const statusClass = item.status_transaksi === 'Selesai' ? 'badge-success' : 
                           item.status_transaksi === 'Dipinjam' ? 'badge-warning' : 'badge-info';
        tr.innerHTML = `
            <td>${item.id_pinjam}</td>
            <td>${item.nama_peminjam || '-'}</td>
            <td>${item.judul_buku || '-'}</td>
            <td>${formatDate(item.tgl_pinjam)}</td>
            <td>${item.tgl_kembali ? formatDate(item.tgl_kembali) : '-'}</td>
            <td><span class="badge ${statusClass}">${item.status_transaksi}</span></td>
            <td>${item.nama_petugas || '-'}</td>
        `;
        tbody.appendChild(tr);
    });
}

function formatDate(dateStr) {
    if (!dateStr) return '-';
    const date = new Date(dateStr);
    return date.toLocaleDateString('id-ID', {
        day: '2-digit',
        month: 'short',
        year: 'numeric'
    });
}

function filterLaporanByStatus(status) {
    if (status === 'all') {
        renderLaporan(allLaporan);
    } else {
        const filtered = allLaporan.filter(item => item.status_transaksi === status);
        renderLaporan(filtered);
    }
}