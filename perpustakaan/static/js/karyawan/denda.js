// Denda page script
document.addEventListener('DOMContentLoaded', function() {
    loadDenda();
});

async function loadDenda() {
    try {
        const data = await apiRequest('/karyawan/denda/api/denda');
        const tbody = document.querySelector('#denda-table tbody');
        
        if (tbody && data.length > 0) {
            tbody.innerHTML = '';
            data.forEach(d => {
                const tr = document.createElement('tr');
                const statusBadge = d.status_bayar === 'Lunas' 
                    ? '<span style="color: green;">Lunas</span>' 
                    : '<span style="color: var(--primary-red);">Belum Lunas</span>';
                
                const actionBtn = d.status_bayar === 'Belum Lunas'
                    ? `<button class="btn btn-primary" onclick="bayarDenda('${d.id_denda}')">Bayar</button>`
                    : '-';
                
                tr.innerHTML = `
                    <td>${d.id_denda}</td>
                    <td>${d.nama_peminjam}</td>
                    <td>${formatCurrency(d.nominal_denda)}</td>
                    <td>${statusBadge}</td>
                    <td>${actionBtn}</td>
                `;
                tbody.appendChild(tr);
            });
        } else if (tbody) {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align: center;">Tidak ada denda</td></tr>';
        }
    } catch (error) {
        console.error('Error loading denda:', error);
    }
}

async function bayarDenda(idDenda) {
    if (!confirm('Konfirmasi pembayaran denda ini?')) return;
    
    try {
        const result = await apiRequest(`/karyawan/denda/api/denda/${idDenda}/bayar`, 'POST');
        if (result.success) {
            showAlert('Pembayaran denda berhasil!', 'success');
            loadDenda();
        }
    } catch (error) {
        showAlert(error.message, 'error');
    }
}
