// Kategori Buku JavaScript

let kategoriData = [];

// Load data on page load
document.addEventListener('DOMContentLoaded', () => {
    loadKategori();
    checkAuth('SPRADM');
});

// Load all categories from API
async function loadKategori() {
    try {
        const response = await fetch('http://localhost:5000/api/admin/kategori', {
            method: 'GET',
            headers: getAuthHeaders()
        });
        
        if (response.ok) {
            const data = await response.json();
            kategoriData = data.kategori || [];
            renderKategoriTable(kategoriData);
        } else {
            showError('Gagal memuat data kategori');
        }
    } catch (error) {
        console.error('Error loading categories:', error);
        showError('Terjadi kesalahan saat memuat data');
    }
}

// Render categories table
function renderKategoriTable(kategoris) {
    const tbody = document.getElementById('kategoriTableBody');
    
    if (kategoris.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="4" style="text-align: center; padding: 40px;">
                    <p style="color: #999;">Tidak ada data kategori</p>
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = kategoris.map(cat => `
        <tr>
            <td><strong>${cat.id_kategori}</strong></td>
            <td>${escapeHtml(cat.nama_kategori)}</td>
            <td><span class="jumlah-badge">${cat.jumlah_buku || 0} buku</span></td>
            <td>
                <div class="action-buttons">
                    <button class="btn-small btn-edit" onclick="editKategori(${cat.id_kategori})">✏️</button>
                    <button class="btn-small btn-delete" onclick="deleteKategori(${cat.id_kategori})">🗑️</button>
                </div>
            </td>
        </tr>
    `).join('');
}

// Search categories
function searchKategori() {
    const searchTerm = document.getElementById('searchKategori').value.toLowerCase();
    
    const filtered = kategoriData.filter(cat => 
        cat.nama_kategori.toLowerCase().includes(searchTerm)
    );
    
    renderKategoriTable(filtered);
}

// Show modal for add/edit
function showModal(mode, katData = null) {
    const modal = document.getElementById('kategoriModal');
    const modalTitle = document.getElementById('modalTitle');
    const formMode = document.getElementById('mode');
    
    formMode.value = mode;
    
    if (mode === 'add') {
        modalTitle.textContent = 'Tambah Kategori Baru';
        document.getElementById('kategoriForm').reset();
        document.getElementById('formIdKategori').disabled = false;
    } else {
        modalTitle.textContent = 'Edit Kategori';
        document.getElementById('formIdKategori').disabled = true;
        
        if (katData) {
            document.getElementById('kategoriIdEdit').value = katData.id_kategori;
            document.getElementById('formIdKategori').value = katData.id_kategori;
            document.getElementById('formNamaKategori').value = katData.nama_kategori;
        }
    }
    
    modal.classList.add('show');
}

// Close modal
function closeModal() {
    const modal = document.getElementById('kategoriModal');
    modal.classList.remove('show');
}

// Save category (add or edit)
async function saveKategori(event) {
    event.preventDefault();
    
    const mode = document.getElementById('mode').value;
    const idEdit = document.getElementById('kategoriIdEdit').value;
    
    const katData = {
        id_kategori: parseInt(document.getElementById('formIdKategori').value),
        nama_kategori: document.getElementById('formNamaKategori').value
    };
    
    try {
        let url, method;
        
        if (mode === 'add') {
            url = 'http://localhost:5000/api/admin/kategori';
            method = 'POST';
        } else {
            url = `http://localhost:5000/api/admin/kategori/${idEdit}`;
            method = 'PUT';
        }
        
        const response = await fetch(url, {
            method: method,
            headers: {
                ...getAuthHeaders(),
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(katData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showSuccess(mode === 'add' ? 'Kategori berhasil ditambahkan' : 'Kategori berhasil diupdate');
            closeModal();
            loadKategori();
        } else {
            showError(result.error || 'Gagal menyimpan kategori');
        }
    } catch (error) {
        console.error('Error saving category:', error);
        showError('Terjadi kesalahan saat menyimpan data');
    }
}

// Edit category
async function editKategori(idKategori) {
    try {
        const response = await fetch(`http://localhost:5000/api/admin/kategori/${idKategori}`, {
            method: 'GET',
            headers: getAuthHeaders()
        });
        
        if (response.ok) {
            const data = await response.json();
            showModal('edit', data.kategori);
        } else {
            showError('Gagal memuat data kategori');
        }
    } catch (error) {
        console.error('Error editing category:', error);
        showError('Terjadi kesalahan');
    }
}

// Delete category
async function deleteKategori(idKategori) {
    if (!confirm('Apakah Anda yakin ingin menghapus kategori ini?')) {
        return;
    }
    
    try {
        const response = await fetch(`http://localhost:5000/api/admin/kategori/${idKategori}`, {
            method: 'DELETE',
            headers: getAuthHeaders()
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showSuccess('Kategori berhasil dihapus');
            loadKategori();
        } else {
            showError(result.error || 'Gagal menghapus kategori');
        }
    } catch (error) {
        console.error('Error deleting category:', error);
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
    const modal = document.getElementById('kategoriModal');
    if (event.target === modal) {
        closeModal();
    }
}
