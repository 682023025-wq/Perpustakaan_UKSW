// Katalog Buku JavaScript
let allBuku = [];
let allKategori = [];

document.addEventListener('DOMContentLoaded', function() {
    loadKategori();
    loadBuku();
    setupFormHandler();
});

function loadKategori() {
    fetch('/api/admin/kategori')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                allKategori = data.kategori;
                populateKategoriSelect();
            }
        })
        .catch(error => console.error('Error loading kategori:', error));
}

function populateKategoriSelect() {
    const selects = [document.getElementById('id_kategori'), document.getElementById('filter-kategori')];
    selects.forEach(select => {
        if (select) {
            select.innerHTML = '<option value="">Pilih Kategori</option>';
            allKategori.forEach(k => {
                select.innerHTML += `<option value="${k.id_kategori}">${k.nama_kategori}</option>`;
            });
        }
    });
}

function loadBuku() {
    fetch('/api/admin/katalog')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                allBuku = data.buku;
                renderBuku(allBuku);
            }
        })
        .catch(error => console.error('Error loading buku:', error));
}

function renderBuku(bukuList) {
    const tbody = document.getElementById('buku-tbody');
    tbody.innerHTML = '';
    
    bukuList.forEach(buku => {
        const tr = document.createElement('tr');
        const kategoriName = allKategori.find(k => k.id_kategori == buku.id_kategori)?.nama_kategori || '-';
        tr.innerHTML = `
            <td>${buku.isbn}</td>
            <td>${buku.judul}</td>
            <td>${buku.pengarang}</td>
            <td>${buku.penerbit}</td>
            <td>${buku.tahun_terbit}</td>
            <td>${kategoriName}</td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="editBuku('${buku.isbn}')">Edit</button>
                <button class="btn btn-sm btn-danger" onclick="deleteBuku('${buku.isbn}')">Hapus</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function setupFormHandler() {
    const form = document.getElementById('buku-form');
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        submitBukuForm();
    });
}

function submitBukuForm() {
    const isEdit = document.getElementById('edit-mode').value === 'true';
    const bukuData = {
        isbn: document.getElementById('isbn').value,
        judul: document.getElementById('judul').value,
        pengarang: document.getElementById('pengarang').value,
        penerbit: document.getElementById('penerbit').value,
        tahun_terbit: parseInt(document.getElementById('tahun_terbit').value),
        id_kategori: parseInt(document.getElementById('id_kategori').value),
        bahasa: document.getElementById('bahasa').value,
        jumlah_halaman: parseInt(document.getElementById('jumlah_halaman').value),
        sinopsis: document.getElementById('sinopsis').value
    };

    const url = isEdit ? '/api/admin/katalog/update' : '/api/admin/katalog/create';
    const method = isEdit ? 'PUT' : 'POST';

    fetch(url, {
        method: method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(bukuData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(isEdit ? 'Buku berhasil diupdate!' : 'Buku berhasil ditambahkan!');
            resetForm();
            loadBuku();
        } else {
            alert('Error: ' + data.message);
        }
    })
    .catch(error => console.error('Error:', error));
}

function editBuku(isbn) {
    const buku = allBuku.find(b => b.isbn === isbn);
    if (buku) {
        document.getElementById('edit-mode').value = 'true';
        document.getElementById('form-title').textContent = 'Edit Buku';
        document.getElementById('isbn').value = buku.isbn;
        document.getElementById('judul').value = buku.judul;
        document.getElementById('pengarang').value = buku.pengarang;
        document.getElementById('penerbit').value = buku.penerbit;
        document.getElementById('tahun_terbit').value = buku.tahun_terbit;
        document.getElementById('id_kategori').value = buku.id_kategori;
        document.getElementById('bahasa').value = buku.bahasa;
        document.getElementById('jumlah_halaman').value = buku.jumlah_halaman;
        document.getElementById('sinopsis').value = buku.sinopsis || '';
        document.getElementById('isbn').disabled = true;
    }
}

function deleteBuku(isbn) {
    if (confirm('Yakin ingin menghapus buku dengan ISBN ' + isbn + '?')) {
        fetch('/api/admin/katalog/delete', {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ isbn: isbn })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Buku berhasil dihapus!');
                loadBuku();
            } else {
                alert('Error: ' + data.message);
            }
        })
        .catch(error => console.error('Error:', error));
    }
}

function resetForm() {
    document.getElementById('edit-mode').value = 'false';
    document.getElementById('form-title').textContent = 'Tambah Buku Baru';
    document.getElementById('buku-form').reset();
    document.getElementById('isbn').disabled = false;
}

function searchBuku() {
    const keyword = document.getElementById('search-input').value.toLowerCase();
    const filtered = allBuku.filter(buku => 
        buku.judul.toLowerCase().includes(keyword) ||
        buku.pengarang.toLowerCase().includes(keyword) ||
        buku.isbn.toLowerCase().includes(keyword)
    );
    renderBuku(filtered);
}

function filterBuku() {
    const kategoriFilter = document.getElementById('filter-kategori').value;
    if (kategoriFilter) {
        const filtered = allBuku.filter(buku => buku.id_kategori == kategoriFilter);
        renderBuku(filtered);
    } else {
        renderBuku(allBuku);
    }
}