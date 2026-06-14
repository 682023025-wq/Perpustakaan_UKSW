// Rak Buku JavaScript

let rakData = [];

// Load data on page load
document.addEventListener('DOMContentLoaded', () => {
    loadRak();
    checkAuth('SPRADM');
});

// Load all rak from API
async function loadRak() {
    try {
        const response = await fetch('http://localhost:5000/api/admin/rak', {
            method: 'GET',
            headers: getAuthHeaders()
        });
        
        if (response.ok) {
            const data = await response.json();
            rakData = data.rak || [];
            renderRakTable(rakData);
        } else {
            showError('Gagal memuat data rak');
        }
    } catch (error) {
        console.error('Error loading rak:', error);
        showError('Terjadi kesalahan saat memuat data');
    }
}

// Render rak table
function renderRakTable(raks) {
    const tbody = document.getElementById('rakTableBody');
    
    if (raks.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="5" style="text-align: center; padding: 40px;">
                    <p style="color: #999;">Tidak ada data rak</p>
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = raks.map(rak => `
        <tr>
            <td><strong>${escapeHtml(rak.id_rak)}</strong></td>
            <td>${escapeHtml(rak.nama_rak)}</td>
            <td>${escapeHtml(rak.lokasi_detail)}</td>
            <td><span class="jumlah-badge">${rak.jumlah_buku || 0} buku</span></td>
            <td>
                <div class="action-buttons">
                    <button class="btn-small btn-edit" onclick="editRak('${rak.id_rak}')">✏️</button>
                    <button class="btn-small btn-delete" onclick="deleteRak('${rak.id_rak}')">🗑️</button>
                </div>
            </td>
        </tr>
    `).join('');
}

// Search rak
function searchRak() {
    const searchTerm = document.getElementById('searchRak').value.toLowerCase();
    
    const filtered = rakData.filter(rak => 
        rak.nama_rak.toLowerCase().includes(searchTerm) ||
        rak.lokasi_detail.toLowerCase().includes(searchTerm) ||
        rak.id_rak.toLowerCase().includes(searchTerm)
    );
    
    renderRakTable(filtered);
}

// Show modal for add/edit
function showModal(mode, rakData = null) {
    const modal = document.getElementById('rakModal');
    const modalTitle = document.getElementById('modalTitle');
    const formMode = document.getElementById('mode');
    
    formMode.value = mode;
    
    if (mode === 'add') {
        modalTitle.textContent = 'Tambah Rak Baru';
        document.getElementById('rakForm').reset();
        document.getElementById('formIdRak').disabled = false;
    } else {
        modalTitle.textContent = 'Edit Rak';
        document.getElementById('formIdRak').disabled = true;
        
        if (rakData) {
            document.getElementById('rakIdEdit').value = rakData.id_rak;
            document.getElementById('formIdRak').value = rakData.id_rak;
            document.getElementById('formNamaRak').value = rakData.nama_rak;
            document.getElementById('formLokasi').value = rakData.lokasi_detail;
        }
    }
    
    modal.classList.add('show');
}

// Close modal
function closeModal() {
    const modal = document.getElementById('rakModal');
    modal.classList.remove('show');
}

// Save rak (add or edit)
async function saveRak(event) {
    event.preventDefault();
    
    const mode = document.getElementById('mode').value;
    const idEdit = document.getElementById('rakIdEdit').value;
    
    const rakData = {
        id_rak: document.getElementById('formIdRak').value,
        nama_rak: document.getElementById('formNamaRak').value,
        lokasi_detail: document.getElementById('formLokasi').value
    };
    
    try {
        let url, method;
        
        if (mode === 'add') {
            url = 'http://localhost:5000/api/admin/rak';
            method = 'POST';
        } else {
            url = `http://localhost:5000/api/admin/rak/${encodeURIComponent(idEdit)}`;
            method = 'PUT';
        }
        
        const response = await fetch(url, {
            method: method,
            headers: {
                ...getAuthHeaders(),
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(rakData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showSuccess(mode === 'add' ? 'Rak berhasil ditambahkan' : 'Rak berhasil diupdate');
            closeModal();
            loadRak();
        } else {
            showError(result.error || 'Gagal menyimpan rak');
        }
    } catch (error) {
        console.error('Error saving rak:', error);
        showError('Terjadi kesalahan saat menyimpan data');
    }
}

// Edit rak
async function editRak(idRak) {
    try {
        const response = await fetch(`http://localhost:5000/api/admin/rak/${encodeURIComponent(idRak)}`, {
            method: 'GET',
            headers: getAuthHeaders()
        });
        
        if (response.ok) {
            const data = await response.json();
            showModal('edit', data.rak);
        } else {
            showError('Gagal memuat data rak');
        }
    } catch (error) {
        console.error('Error editing rak:', error);
        showError('Terjadi kesalahan');
    }
}

// Delete rak
async function deleteRak(idRak) {
    if (!confirm('Apakah Anda yakin ingin menghapus rak ini?')) {
        return;
    }
    
    try {
        const response = await fetch(`http://localhost:5000/api/admin/rak/${encodeURIComponent(idRak)}`, {
            method: 'DELETE',
            headers: getAuthHeaders()
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showSuccess('Rak berhasil dihapus');
            loadRak();
        } else {
            showError(result.error || 'Gagal menghapus rak');
        }
    } catch (error) {
        console.error('Error deleting rak:', error);
        showError('Terjadi kesalahan saat menghapus data');
    }
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('rakModal');
    if (event.target === modal) {
        closeModal();
    }
}
