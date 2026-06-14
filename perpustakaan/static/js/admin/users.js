// Users Management JavaScript
let allUsers = [];

document.addEventListener('DOMContentLoaded', function() {
    loadUsers();
    setupFormHandler();
});

function loadUsers() {
    fetch('/api/admin/users')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                allUsers = data.users;
                renderUsers(allUsers);
            }
        })
        .catch(error => console.error('Error loading users:', error));
}

function renderUsers(users) {
    const tbody = document.getElementById('users-tbody');
    tbody.innerHTML = '';
    
    users.forEach(user => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${user.id_user}</td>
            <td>${user.username}</td>
            <td>${user.nama_lengkap}</td>
            <td>${user.email}</td>
            <td>${user.id_role}</td>
            <td><span class="badge ${user.status_aktif === 'Aktif' ? 'badge-success' : 'badge-danger'}">${user.status_aktif}</span></td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="editUser('${user.id_user}')">Edit</button>
                <button class="btn btn-sm btn-danger" onclick="deleteUser('${user.id_user}')">Hapus</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function setupFormHandler() {
    const form = document.getElementById('user-form');
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        submitUserForm();
    });
}

function submitUserForm() {
    const isEdit = document.getElementById('edit-mode').value === 'true';
    const userData = {
        id_user: document.getElementById('id_user').value,
        username: document.getElementById('username').value,
        password: document.getElementById('password').value,
        nama_lengkap: document.getElementById('nama_lengkap').value,
        email: document.getElementById('email').value,
        no_telepon: document.getElementById('no_telepon').value,
        id_role: document.getElementById('id_role').value,
        program_studi: document.getElementById('program_studi').value,
        fakultas: document.getElementById('fakultas').value,
        status_aktif: document.getElementById('status_aktif').value
    };

    const url = isEdit ? '/api/admin/users/update' : '/api/admin/users/create';
    const method = isEdit ? 'PUT' : 'POST';

    fetch(url, {
        method: method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(isEdit ? 'User berhasil diupdate!' : 'User berhasil ditambahkan!');
            resetForm();
            loadUsers();
        } else {
            alert('Error: ' + data.message);
        }
    })
    .catch(error => console.error('Error:', error));
}

function editUser(idUser) {
    const user = allUsers.find(u => u.id_user === idUser);
    if (user) {
        document.getElementById('edit-mode').value = 'true';
        document.getElementById('form-title').textContent = 'Edit User';
        document.getElementById('id_user').value = user.id_user;
        document.getElementById('username').value = user.username;
        document.getElementById('password').value = '';
        document.getElementById('nama_lengkap').value = user.nama_lengkap;
        document.getElementById('email').value = user.email;
        document.getElementById('no_telepon').value = user.no_telepon;
        document.getElementById('id_role').value = user.id_role;
        document.getElementById('program_studi').value = user.program_studi || '';
        document.getElementById('fakultas').value = user.fakultas || '';
        document.getElementById('status_aktif').value = user.status_aktif;
        document.getElementById('id_user').disabled = true;
    }
}

function deleteUser(idUser) {
    if (confirm('Yakin ingin menghapus user ' + idUser + '?')) {
        fetch('/api/admin/users/delete', {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id_user: idUser })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('User berhasil dihapus!');
                loadUsers();
            } else {
                alert('Error: ' + data.message);
            }
        })
        .catch(error => console.error('Error:', error));
    }
}

function resetForm() {
    document.getElementById('edit-mode').value = 'false';
    document.getElementById('form-title').textContent = 'Tambah User Baru';
    document.getElementById('user-form').reset();
    document.getElementById('id_user').disabled = false;
}

function searchUser() {
    const keyword = document.getElementById('search-input').value.toLowerCase();
    const filtered = allUsers.filter(user => 
        user.nama_lengkap.toLowerCase().includes(keyword) ||
        user.username.toLowerCase().includes(keyword) ||
        user.id_user.toLowerCase().includes(keyword)
    );
    renderUsers(filtered);
}

function filterUsers() {
    const roleFilter = document.getElementById('filter-role').value;
    if (roleFilter) {
        const filtered = allUsers.filter(user => user.id_role === roleFilter);
        renderUsers(filtered);
    } else {
        renderUsers(allUsers);
    }
}