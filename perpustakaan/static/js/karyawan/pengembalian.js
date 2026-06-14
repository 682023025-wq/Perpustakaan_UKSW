// Pengembalian page script
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('pengembalian-form');
    
    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const idPinjam = document.getElementById('id_pinjam').value.trim();
            
            try {
                const result = await apiRequest('/karyawan/denda/api/pengembalian/proses', 'POST', {
                    id_pinjam: idPinjam
                });
                
                if (result.success) {
                    let message = `Pengembalian berhasil!`;
                    if (result.denda > 0) {
                        message += ` Terdapat denda: ${formatCurrency(result.denda)}`;
                    }
                    showAlert(message, 'success');
                    form.reset();
                }
            } catch (error) {
                showAlert(error.message, 'error');
            }
        });
    }
});
