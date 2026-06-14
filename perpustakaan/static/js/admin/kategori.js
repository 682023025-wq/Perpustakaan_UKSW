// Kategori JavaScript
let allKategori = [];

document.addEventListener('DOMContentLoaded', function() {
    loadKategori();
    setupFormHandler();
});

function loadKategori() {
    fetch('/api/admin/kategori')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                allKategori = data.kategori;
                renderKategori(allKategori);
            }
        })
        .catch(error => console.error('Error loading kategori:', error));
}

function renderKategori(kategoriList) {
    const tbody = document.getElementById('kategori-tbody');
    tbody.innerHTML = '';
    
    kategoriList.forEach(kategori => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${kategori.id_kategori}</td>
            <td>${kategori.nama_kategori}</td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="editKategori(${kategori.id_kategori})">Edit</button>
                <button class="btn btn-sm btn-danger" onclick="deleteKategori(${kategori.id_kategori})">Hapus</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function setupFormHandler() {
    const form = document.getElementById('kategori-form');
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        submitKategoriForm();
    });
}

function submitKategoriForm() {
    const isEdit = document.getElementById('edit-mode').value === 'true';
    const kategoriData = {
        id_kategori: parseInt(document.getElementById('id_kategori').value),
        nama_kategori: document.getElementById('nama_kategori').value
    };

    const url = isEdit ? '/api/admin/kategori/update' : '/api/admin/kategori/create';
    const method = isEdit ? 'PUT' : 'POST';

    fetch(url, {
        method: method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(kategoriData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(isEdit ? 'Kategori berhasil diupdate!' : 'Kategori berhasil ditambahkan!');
            resetForm();
            loadKategori();
        } else {
            alert('Error: ' + data.message);
        }
    })
    .catch(error => console.error('Error:', error));
}

function editKategori(idKategori) {
    const kategori = allKategori.find(k => k.id_kategori == idKategori);
    if (kategori) {
        document.getElementById('edit-mode').value = 'true';
        document.getElementById('form-title').textContent = 'Edit Kategori';
        document.getElementById('id_kategori').value = kategori.id_kategori;
        document.getElementById('nama_kategori').value = kategori.nama_kategori;
        document.getElementById('id_kategori').disabled = true;
    }
}

function deleteKategori(idKategori) {
    if (confirm('Yakin ingin menghapus kategori ini?')) {
        fetch('/api/admin/kategori/delete', {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id_kategori: idKategori })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Kategori berhasil dihapus!');
                loadKategori();
            } else {
                alert('Error: ' + data.message);
            }
        })
        .catch(error => console.error('Error:', error));
    }
}

function resetForm() {
    document.getElementById('edit-mode').value = 'false';
    document.getElementById('form-title').textContent = 'Tambah Kategori Baru';
    document.getElementById('kategori-form').reset();
    document.getElementById('id_kategori').disabled = false;
}