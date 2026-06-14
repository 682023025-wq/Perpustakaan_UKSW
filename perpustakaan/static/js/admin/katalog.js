// Katalog Buku JavaScript

let booksData = [];
let categoriesData = [];

// Load data on page load
document.addEventListener('DOMContentLoaded', () => {
    loadCategories();
    loadBooks();
    checkAuth('SPRADM');
});

// Load categories for dropdown
async function loadCategories() {
    try {
        const response = await fetch('http://localhost:5000/api/admin/kategori', {
            method: 'GET',
            headers: getAuthHeaders()
        });
        
        if (response.ok) {
            const data = await response.json();
            categoriesData = data.kategori || [];
            populateCategoryDropdowns();
        }
    } catch (error) {
        console.error('Error loading categories:', error);
    }
}

// Populate category dropdowns
function populateCategoryDropdowns() {
    const filterSelect = document.getElementById('filterKategori');
    const formSelect = document.getElementById('formKategori');
    
    // Clear existing options except first
    filterSelect.innerHTML = '<option value="">Semua Kategori</option>';
    formSelect.innerHTML = '';
    
    categoriesData.forEach(cat => {
        filterSelect.innerHTML += `<option value="${cat.id_kategori}">${cat.nama_kategori}</option>`;
        formSelect.innerHTML += `<option value="${cat.id_kategori}">${cat.nama_kategori}</option>`;
    });
}

// Load all books from API
async function loadBooks() {
    try {
        const kategoriFilter = document.getElementById('filterKategori').value;
        
        let url = 'http://localhost:5000/api/admin/katalog';
        const params = new URLSearchParams();
        
        if (kategoriFilter) params.append('kategori', kategoriFilter);
        
        if (params.toString()) {
            url += '?' + params.toString();
        }
        
        const response = await fetch(url, {
            method: 'GET',
            headers: getAuthHeaders()
        });
        
        if (response.ok) {
            const data = await response.json();
            booksData = data.buku || [];
            renderBooksTable(booksData);
        } else {
            showError('Gagal memuat data buku');
        }
    } catch (error) {
        console.error('Error loading books:', error);
        showError('Terjadi kesalahan saat memuat data');
    }
}

// Render books table
function renderBooksTable(books) {
    const tbody = document.getElementById('booksTableBody');
    
    if (books.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" style="text-align: center; padding: 40px;">
                    <p style="color: #999;">Tidak ada data buku</p>
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = books.map(book => `
        <tr>
            <td><strong>${escapeHtml(book.isbn)}</strong></td>
            <td>${escapeHtml(book.judul)}</td>
            <td>${escapeHtml(book.pengarang)}</td>
            <td>${escapeHtml(book.penerbit)}</td>
            <td>${book.tahun_terbit}</td>
            <td><span class="role-badge">${getCategoryName(book.id_kategori)}</span></td>
            <td>
                <span class="stok-badge stok-tersedia">
                    ${book.stok || 0} Tersedia
                </span>
            </td>
            <td>
                <div class="action-buttons">
                    <button class="btn-small btn-view" onclick="viewBook('${book.isbn}')">👁️</button>
                    <button class="btn-small btn-edit" onclick="editBook('${book.isbn}')">✏️</button>
                    <button class="btn-small btn-delete" onclick="deleteBook('${book.isbn}')">🗑️</button>
                </div>
            </td>
        </tr>
    `).join('');
}

// Search books
function searchBooks() {
    const searchTerm = document.getElementById('searchBook').value.toLowerCase();
    
    const filtered = booksData.filter(book => 
        book.judul.toLowerCase().includes(searchTerm) ||
        book.pengarang.toLowerCase().includes(searchTerm) ||
        book.isbn.toLowerCase().includes(searchTerm) ||
        book.penerbit.toLowerCase().includes(searchTerm)
    );
    
    renderBooksTable(filtered);
}

// Get category name
function getCategoryName(idKategori) {
    const cat = categoriesData.find(c => c.id_kategori == idKategori);
    return cat ? cat.nama_kategori : idKategori;
}

// Show modal for add/edit
function showModal(mode, bookData = null) {
    const modal = document.getElementById('bookModal');
    const modalTitle = document.getElementById('modalTitle');
    const formMode = document.getElementById('mode');
    
    formMode.value = mode;
    
    if (mode === 'add') {
        modalTitle.textContent = 'Tambah Buku Baru';
        document.getElementById('bookForm').reset();
        document.getElementById('formIsbn').disabled = false;
    } else {
        modalTitle.textContent = 'Edit Buku';
        document.getElementById('formIsbn').disabled = true;
        
        if (bookData) {
            document.getElementById('isbnEdit').value = bookData.isbn;
            document.getElementById('formIsbn').value = bookData.isbn;
            document.getElementById('formJudul').value = bookData.judul;
            document.getElementById('formPengarang').value = bookData.pengarang;
            document.getElementById('formPenerbit').value = bookData.penerbit;
            document.getElementById('formTahunTerbit').value = bookData.tahun_terbit;
            document.getElementById('formBahasa').value = bookData.bahasa;
            document.getElementById('formHalaman').value = bookData.jumlah_halaman;
            document.getElementById('formSinopsis').value = bookData.sinopsis || '';
            document.getElementById('formCover').value = bookData.url_cover || '';
            document.getElementById('formKategori').value = bookData.id_kategori;
        }
    }
    
    modal.classList.add('show');
}

// Close modal
function closeModal() {
    const modal = document.getElementById('bookModal');
    modal.classList.remove('show');
}

// Save book (add or edit)
async function saveBook(event) {
    event.preventDefault();
    
    const mode = document.getElementById('mode').value;
    const isbnEdit = document.getElementById('isbnEdit').value;
    
    const bookData = {
        isbn: document.getElementById('formIsbn').value,
        judul: document.getElementById('formJudul').value,
        pengarang: document.getElementById('formPengarang').value,
        penerbit: document.getElementById('formPenerbit').value,
        tahun_terbit: parseInt(document.getElementById('formTahunTerbit').value),
        bahasa: document.getElementById('formBahasa').value,
        jumlah_halaman: parseInt(document.getElementById('formHalaman').value),
        sinopsis: document.getElementById('formSinopsis').value,
        url_cover: document.getElementById('formCover').value,
        id_kategori: parseInt(document.getElementById('formKategori').value)
    };
    
    try {
        let url, method;
        
        if (mode === 'add') {
            url = 'http://localhost:5000/api/admin/katalog';
            method = 'POST';
        } else {
            url = `http://localhost:5000/api/admin/katalog/${isbnEdit}`;
            method = 'PUT';
        }
        
        const response = await fetch(url, {
            method: method,
            headers: {
                ...getAuthHeaders(),
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(bookData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showSuccess(mode === 'add' ? 'Buku berhasil ditambahkan' : 'Buku berhasil diupdate');
            closeModal();
            loadBooks();
        } else {
            showError(result.error || 'Gagal menyimpan buku');
        }
    } catch (error) {
        console.error('Error saving book:', error);
        showError('Terjadi kesalahan saat menyimpan data');
    }
}

// View book details
async function viewBook(isbn) {
    try {
        const response = await fetch(`http://localhost:5000/api/admin/katalog/${isbn}`, {
            method: 'GET',
            headers: getAuthHeaders()
        });
        
        if (response.ok) {
            const data = await response.json();
            const book = data.buku;
            
            alert(`
DETAIL BUKU
-----------
ISBN: ${book.isbn}
Judul: ${book.judul}
Pengarang: ${book.pengarang}
Penerbit: ${book.penerbit}
Tahun Terbit: ${book.tahun_terbit}
Bahasa: ${book.bahasa}
Jumlah Halaman: ${book.jumlah_halaman}
Kategori: ${getCategoryName(book.id_kategori)}
Sinopsis: ${book.sinopsis || '-'}
            `.trim());
        } else {
            showError('Gagal memuat detail buku');
        }
    } catch (error) {
        console.error('Error viewing book:', error);
        showError('Terjadi kesalahan');
    }
}

// Edit book
async function editBook(isbn) {
    try {
        const response = await fetch(`http://localhost:5000/api/admin/katalog/${isbn}`, {
            method: 'GET',
            headers: getAuthHeaders()
        });
        
        if (response.ok) {
            const data = await response.json();
            showModal('edit', data.buku);
        } else {
            showError('Gagal memuat data buku');
        }
    } catch (error) {
        console.error('Error editing book:', error);
        showError('Terjadi kesalahan');
    }
}

// Delete book
async function deleteBook(isbn) {
    if (!confirm('Apakah Anda yakin ingin menghapus buku ini?')) {
        return;
    }
    
    try {
        const response = await fetch(`http://localhost:5000/api/admin/katalog/${isbn}`, {
            method: 'DELETE',
            headers: getAuthHeaders()
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showSuccess('Buku berhasil dihapus');
            loadBooks();
        } else {
            showError(result.error || 'Gagal menghapus buku');
        }
    } catch (error) {
        console.error('Error deleting book:', error);
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
    const modal = document.getElementById('bookModal');
    if (event.target === modal) {
        closeModal();
    }
}
