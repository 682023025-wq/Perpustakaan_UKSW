// Rak JavaScript
let allRak = [];

document.addEventListener('DOMContentLoaded', function() {
    loadRak();
    setupFormHandler();
});

function loadRak() {
    fetch('/api/admin/rak')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                allRak = data.rak;
                renderRak(allRak);
            }
        })
        .catch(error => console.error('Error loading rak:', error));
}

function renderRak(rakList) {
    const tbody = document.getElementById('rak-tbody');
    tbody.innerHTML = '';
    
    rakList.forEach(rak => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${rak.id_rak}</td>
            <td>${rak.nama_rak}</td>
            <td>${rak.lokasi_detail}</td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="editRak('${rak.id_rak}')">Edit</button>
                <button class="btn btn-sm btn-danger" onclick="deleteRak('${rak.id_rak}')">Hapus</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function setupFormHandler() {
    const form = document.getElementById('rak-form');
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        submitRakForm();
    });
}

function submitRakForm() {
    const isEdit = document.getElementById('edit-mode').value === 'true';
    const rakData = {
        id_rak: document.getElementById('id_rak').value,
        nama_rak: document.getElementById('nama_rak').value,
        lokasi_detail: document.getElementById('lokasi_detail').value
    };

    const url = isEdit ? '/api/admin/rak/update' : '/api/admin/rak/create';
    const method = isEdit ? 'PUT' : 'POST';

    fetch(url, {
        method: method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(rakData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(isEdit ? 'Rak berhasil diupdate!' : 'Rak berhasil ditambahkan!');
            resetForm();
            loadRak();
        } else {
            alert('Error: ' + data.message);
        }
    })
    .catch(error => console.error('Error:', error));
}

function editRak(idRak) {
    const rak = allRak.find(r => r.id_rak === idRak);
    if (rak) {
        document.getElementById('edit-mode').value = 'true';
        document.getElementById('form-title').textContent = 'Edit Rak';
        document.getElementById('id_rak').value = rak.id_rak;
        document.getElementById('nama_rak').value = rak.nama_rak;
        document.getElementById('lokasi_detail').value = rak.lokasi_detail;
        document.getElementById('id_rak').disabled = true;
    }
}

function deleteRak(idRak) {
    if (confirm('Yakin ingin menghapus rak ' + idRak + '?')) {
        fetch('/api/admin/rak/delete', {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id_rak: idRak })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Rak berhasil dihapus!');
                loadRak();
            } else {
                alert('Error: ' + data.message);
            }
        })
        .catch(error => console.error('Error:', error));
    }
}

function resetForm() {
    document.getElementById('edit-mode').value = 'false';
    document.getElementById('form-title').textContent = 'Tambah Rak Baru';
    document.getElementById('rak-form').reset();
    document.getElementById('id_rak').disabled = false;
}