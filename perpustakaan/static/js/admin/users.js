// Users Management JavaScript

let usersData = [];

// Load users on page load
document.addEventListener('DOMContentLoaded', () => {
    loadUsers();
    checkAuth('SPRADM');
});

// Load all users from API
async function loadUsers() {
    try {
        const roleFilter = document.getElementById('filterRole').value;
        const statusFilter = document.getElementById('filterStatus').value;
        
        let url = 'http://localhost:5000/api/admin/users';
        const params = new URLSearchParams();
        
        if (roleFilter) params.append('role', roleFilter);
        if (statusFilter) params.append('status', statusFilter);
        
        if (params.toString()) {
            url += '?' + params.toString();
        }
        
        const response = await fetch(url, {
            method: 'GET',
            headers: getAuthHeaders()
        });
        
        if (response.ok) {
            const data = await response.json();
            usersData = data.users || [];
            renderUsersTable(usersData);
        } else {
            showError('Gagal memuat data users');
        }
    } catch (error) {
        console.error('Error loading users:', error);
        showError('Terjadi kesalahan saat memuat data');
    }
}

// Render users table
function renderUsersTable(users) {
    const tbody = document.getElementById('usersTableBody');
    
    if (users.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" style="text-align: center; padding: 40px;">
                    <p style="color: #999;">Tidak ada data users</p>
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = users.map(user => `
        <tr>
            <td><strong>${escapeHtml(user.id_user)}</strong></td>
            <td>${escapeHtml(user.nama_lengkap)}</td>
            <td>${escapeHtml(user.username)}</td>
            <td>${escapeHtml(user.email)}</td>
            <td><span class="role-badge">${getRoleName(user.id_role)}</span></td>
            <td>
                <span class="status-badge ${user.status_aktif === 'Aktif' ? 'status-aktif' : 'status-nonaktif'}">
                    ${user.status_aktif}
                </span>
            </td>
            <td>
                <div class="action-buttons">
                    <button class="btn-small btn-view" onclick="viewUser('${user.id_user}')">👁️</button>
                    <button class="btn-small btn-edit" onclick="editUser('${user.id_user}')">✏️</button>
                    <button class="btn-small btn-delete" onclick="deleteUser('${user.id_user}')">🗑️</button>
                </div>
            </td>
        </tr>
    `).join('');
}

// Search users
function searchUsers() {
    const searchTerm = document.getElementById('searchUser').value.toLowerCase();
    
    const filtered = usersData.filter(user => 
        user.nama_lengkap.toLowerCase().includes(searchTerm) ||
        user.email.toLowerCase().includes(searchTerm) ||
        user.username.toLowerCase().includes(searchTerm) ||
        user.id_user.toLowerCase().includes(searchTerm)
    );
    
    renderUsersTable(filtered);
}

// Get role name
function getRoleName(roleId) {
    const roles = {
        'SPRADM': 'Super Admin',
        'PTGS': 'Petugas',
        'DSN': 'Dosen',
        'MHS': 'Mahasiswa'
    };
    return roles[roleId] || roleId;
}

// Show modal for add/edit
function showModal(mode, userData = null) {
    const modal = document.getElementById('userModal');
    const modalTitle = document.getElementById('modalTitle');
    const formMode = document.getElementById('mode');
    
    formMode.value = mode;
    
    if (mode === 'add') {
        modalTitle.textContent = 'Tambah User Baru';
        document.getElementById('userForm').reset();
        document.getElementById('formIdUser').disabled = false;
    } else {
        modalTitle.textContent = 'Edit User';
        document.getElementById('formIdUser').disabled = true;
        
        if (userData) {
            document.getElementById('userId').value = userData.id_user;
            document.getElementById('formIdUser').value = userData.id_user;
            document.getElementById('formUsername').value = userData.username;
            document.getElementById('formPassword').value = '';
            document.getElementById('formNamaLengkap').value = userData.nama_lengkap;
            document.getElementById('formEmail').value = userData.email;
            document.getElementById('formNoTelepon').value = userData.no_telepon;
            document.getElementById('formProdi').value = userData.program_studi || '';
            document.getElementById('formFakultas').value = userData.fakultas || '';
            document.getElementById('formRole').value = userData.id_role;
            document.getElementById('formStatus').value = userData.status_aktif;
        }
    }
    
    modal.classList.add('show');
}

// Close modal
function closeModal() {
    const modal = document.getElementById('userModal');
    modal.classList.remove('show');
}

// Save user (add or edit)
async function saveUser(event) {
    event.preventDefault();
    
    const mode = document.getElementById('mode').value;
    const userId = document.getElementById('userId').value;
    
    const userData = {
        id_user: document.getElementById('formIdUser').value,
        username: document.getElementById('formUsername').value,
        nama_lengkap: document.getElementById('formNamaLengkap').value,
        email: document.getElementById('formEmail').value,
        no_telepon: document.getElementById('formNoTelepon').value,
        program_studi: document.getElementById('formProdi').value,
        fakultas: document.getElementById('formFakultas').value,
        id_role: document.getElementById('formRole').value,
        status_aktif: document.getElementById('formStatus').value
    };
    
    const password = document.getElementById('formPassword').value;
    if (password) {
        userData.password = password;
    }
    
    try {
        let url, method;
        
        if (mode === 'add') {
            url = 'http://localhost:5000/api/admin/users';
            method = 'POST';
        } else {
            url = `http://localhost:5000/api/admin/users/${userId}`;
            method = 'PUT';
        }
        
        const response = await fetch(url, {
            method: method,
            headers: {
                ...getAuthHeaders(),
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(userData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showSuccess(mode === 'add' ? 'User berhasil ditambahkan' : 'User berhasil diupdate');
            closeModal();
            loadUsers();
        } else {
            showError(result.error || 'Gagal menyimpan user');
        }
    } catch (error) {
        console.error('Error saving user:', error);
        showError('Terjadi kesalahan saat menyimpan data');
    }
}

// View user details
async function viewUser(userId) {
    try {
        const response = await fetch(`http://localhost:5000/api/admin/users/${userId}`, {
            method: 'GET',
            headers: getAuthHeaders()
        });
        
        if (response.ok) {
            const data = await response.json();
            const user = data.user;
            
            alert(`
DETAIL USER
-----------
ID User: ${user.id_user}
Nama: ${user.nama_lengkap}
Username: ${user.username}
Email: ${user.email}
No. Telepon: ${user.no_telepon}
Program Studi: ${user.program_studi || '-'}
Fakultas: ${user.fakultas || '-'}
Role: ${getRoleName(user.id_role)}
Status: ${user.status_aktif}
Created: ${new Date(user.created_at).toLocaleDateString('id-ID')}
            `.trim());
        } else {
            showError('Gagal memuat detail user');
        }
    } catch (error) {
        console.error('Error viewing user:', error);
        showError('Terjadi kesalahan');
    }
}

// Edit user
async function editUser(userId) {
    try {
        const response = await fetch(`http://localhost:5000/api/admin/users/${userId}`, {
            method: 'GET',
            headers: getAuthHeaders()
        });
        
        if (response.ok) {
            const data = await response.json();
            showModal('edit', data.user);
        } else {
            showError('Gagal memuat data user');
        }
    } catch (error) {
        console.error('Error editing user:', error);
        showError('Terjadi kesalahan');
    }
}

// Delete user
async function deleteUser(userId) {
    if (!confirm('Apakah Anda yakin ingin menghapus user ini?')) {
        return;
    }
    
    try {
        const response = await fetch(`http://localhost:5000/api/admin/users/${userId}`, {
            method: 'DELETE',
            headers: getAuthHeaders()
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showSuccess('User berhasil dihapus');
            loadUsers();
        } else {
            showError(result.error || 'Gagal menghapus user');
        }
    } catch (error) {
        console.error('Error deleting user:', error);
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
    const modal = document.getElementById('userModal');
    if (event.target === modal) {
        closeModal();
    }
}
