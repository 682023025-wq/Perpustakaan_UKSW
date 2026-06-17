let allUsers = [];

// 1. Load Data Users dari Backend
async function loadUsers() {
    try {
        const response = await fetch('/admin/users/api/users');
        allUsers = await response.json();
        applyFilters(); // Render tabel dengan filter aktif
    } catch (error) {
        console.error('Error loading users:', error);
        alert('Gagal memuat data users');
    }
}

// 2. Render Tabel dan Handle Search/Filter
function applyFilters() {
    const keyword = document.getElementById('search-input').value.toLowerCase();
    const roleFilter = document.getElementById('filter-role').value;
    
    const filtered = allUsers.filter(user => {
        const matchKeyword = !keyword || 
            user.nama_lengkap.toLowerCase().includes(keyword) ||
            user.username.toLowerCase().includes(keyword) ||
            user.email.toLowerCase().includes(keyword);
            
        const matchRole = !roleFilter || user.id_role === roleFilter;
        
        return matchKeyword && matchRole;
    });
    
    renderTable(filtered);
}

function renderTable(users) {
    const tbody = document.getElementById('users-tbody');
    tbody.innerHTML = '';
    
    if (users.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align:center; padding:20px;">Tidak ada data user</td></tr>';
        return;
    }

    users.forEach(user => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${user.id_user}</td>
            <td>${user.username}</td>
            <td>${user.nama_lengkap}</td>
            <td>${user.email}</td>
            <td><span class="badge role-${user.id_role.toLowerCase()}">${user.nama_role}</span></td>
            <td><span class="badge status-${user.status_aktif ? user.status_aktif.toLowerCase() : 'aktif'}">${user.status_aktif || 'Aktif'}</span></td>
            <td class="action-buttons">
                <button class="btn btn-sm btn-warning" onclick="editUser('${user.id_user}')">Edit</button>
                ${user.status_aktif === 'Aktif' ? `<button class="btn btn-sm btn-danger" onclick="deactivateUser('${user.id_user}', '${user.nama_lengkap}')">Nonaktifkan</button>` : '<span class="text-muted">Nonaktif</span>'}
            </td>
        `;
        tbody.appendChild(tr);
    });
}

// Fungsi dummy untuk onkeyup/onchange di HTML (didelegasikan ke applyFilters)
function searchUser() { applyFilters(); }
function filterUsers() { applyFilters(); }

// 3. Handle Submit Form (Tambah / Edit)
async function handleFormSubmit(event) {
    event.preventDefault(); // Mencegah page reload
    const isEdit = document.getElementById('edit-mode').value === 'true';
    const idUser = document.getElementById('id_user').value;
    
    const payload = {
        username: document.getElementById('username').value,
        nama_lengkap: document.getElementById('nama_lengkap').value,
        email: document.getElementById('email').value,
        no_telepon: document.getElementById('no_telepon').value,
        id_role: document.getElementById('id_role').value,
        status_aktif: document.getElementById('status_aktif').value,
        program_studi: document.getElementById('program_studi').value,
        fakultas: document.getElementById('fakultas').value,
        password: document.getElementById('password').value
    };

    let url = '/admin/users/api/users';
    let method = 'POST';
    
    if (isEdit) {
        url = `/admin/users/api/users/${idUser}`;
        method = 'PUT';
        if (!payload.password) delete payload.password; // Jangan kirim password kosong saat edit
    } else {
        payload.id_user = idUser;
        if (!payload.password) {
            alert('Password wajib diisi untuk user baru!');
            return;
        }
    }

    try {
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const result = await response.json();
        
        if (result.success) {
            alert(result.message || 'Data berhasil disimpan!');
            resetForm();
            loadUsers(); // Refresh tabel
        } else {
            alert('Gagal: ' + (result.error || 'Terjadi kesalahan'));
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

// 4. Fitur Edit User
function editUser(idUser) {
    const user = allUsers.find(u => u.id_user === idUser);
    if (!user) return;

    document.getElementById('edit-mode').value = 'true';
    document.getElementById('form-title').innerText = 'Edit User: ' + user.nama_lengkap;
    
    document.getElementById('id_user').value = user.id_user;
    document.getElementById('id_user').disabled = true; // ID tidak boleh diubah
    
    document.getElementById('username').value = user.username;
    document.getElementById('username').disabled = true; // Username dikunci saat edit
    document.getElementById('nama_lengkap').value = user.nama_lengkap;
    document.getElementById('email').value = user.email;
    document.getElementById('no_telepon').value = user.no_telepon;
    document.getElementById('id_role').value = user.id_role;
    document.getElementById('status_aktif').value = user.status_aktif;
    document.getElementById('program_studi').value = user.program_studi || '';
    document.getElementById('fakultas').value = user.fakultas || '';
    
    document.getElementById('password').value = ''; 
    document.getElementById('password').required = false; // Password tidak wajib saat edit
    
    // Scroll ke form
    document.getElementById('user-form').scrollIntoView({ behavior: 'smooth' });
}

// 5. Fitur Nonaktifkan User
async function deactivateUser(idUser, namaLengkap) {
    const alasan = prompt(`Masukkan alasan menonaktifkan user ${namaLengkap}:`);
    if (!alasan) return; // Batal jika user klik cancel

    try {
        const response = await fetch(`/admin/users/api/users/${idUser}/deactivate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ alasan: alasan })
        });
        const result = await response.json();
        
        if (result.success) {
            alert('User berhasil dinonaktifkan');
            loadUsers(); // Refresh tabel
        } else {
            alert('Gagal: ' + result.error);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

// 6. Reset Form
function resetForm() {
    document.getElementById('user-form').reset();
    document.getElementById('edit-mode').value = 'false';
    document.getElementById('form-title').innerText = 'Tambah User Baru';
    document.getElementById('id_user').disabled = false;
    document.getElementById('username').disabled = false;
    document.getElementById('password').required = true;
}

// Inisialisasi saat halaman dimuat
document.addEventListener('DOMContentLoaded', () => {
    loadUsers();
});