"""
Aplikasi Sistem Informasi Perpustakaan
Flask Backend API
"""
from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
import os
from config import Config
from backend.auth import login_user, logout_user, login_required, admin_required, karyawan_required
from backend.admin.dashboard import get_dashboard_stats as admin_get_stats, get_recent_activities
from backend.admin.users import get_all_users, get_user_by_id, create_user, update_user, delete_user, reset_password
from backend.admin.katalog import get_all_buku, get_buku_by_id, create_buku, update_buku, delete_buku, add_item_buku, search_buku
from backend.admin.kategori import get_all_kategori, get_kategori_by_id, create_kategori, update_kategori, delete_kategori
from backend.admin.rak import get_all_rak, get_rak_by_id, create_rak, update_rak, delete_rak
from backend.karyawan.dashboard import get_dashboard_stats as karyawan_get_stats, get_peminjaman_perlu_dikembalikan
from backend.karyawan.peminjaman import proses_peminjaman, proses_pengembalian, get_detail_peminjaman, get_riwayat_peminjaman
from backend.karyawan.denda import get_all_denda, bayar_denda, get_statistik_denda
from backend.karyawan.laporan import get_laporan_peminjaman, get_laporan_pengembalian, get_laporan_denda, get_statistik_bulanan

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.config.from_object(Config)
CORS(app, supports_credentials=True)

# ==================== AUTH ROUTES ====================

@app.route('/')
def index():
    """Serve login page"""
    return send_from_directory('frontend', 'login.html')

@app.route('/api/login', methods=['POST'])
def login():
    """Endpoint login"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    result = login_user(username, password)
    
    if result['success']:
        session['user_id'] = result['user']['id_user']
        session['username'] = result['user']['username']
        session['nama'] = result['user']['nama']
        session['role'] = result['user']['role']
        
        return jsonify({
            'success': True,
            'message': 'Login berhasil',
            'redirect': '/admin/dashboard.html' if result['user']['role'] == 'ADMIN' else '/karyawan/dashboard.html'
        })
    
    return jsonify(result), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    """Endpoint logout"""
    result = logout_user()
    session.clear()
    return jsonify(result)

@app.route('/api/me', methods=['GET'])
@login_required
def get_current_user():
    """Get current logged in user info"""
    return jsonify({
        'user_id': session.get('user_id'),
        'username': session.get('username'),
        'nama': session.get('nama'),
        'role': session.get('role')
    })

# ==================== ADMIN ROUTES ====================

@app.route('/admin/<path:path>')
def serve_admin(path):
    """Serve admin frontend files"""
    return send_from_directory('frontend/admin', path)

@app.route('/karyawan/<path:path>')
def serve_karyawan(path):
    """Serve karyawan frontend files"""
    return send_from_directory('frontend/karyawan', path)

@app.route('/api/admin/dashboard/stats', methods=['GET'])
@admin_required
def admin_dashboard_stats():
    """Get admin dashboard statistics"""
    stats = admin_get_stats()
    return jsonify(stats)

@app.route('/api/admin/users', methods=['GET'])
@admin_required
def api_get_users():
    """Get all users with optional filters"""
    role = request.args.get('role')
    status = request.args.get('status')
    result = get_all_users(role, status)
    return jsonify(result)

@app.route('/api/admin/users/<id_user>', methods=['GET'])
@admin_required
def api_get_user(id_user):
    """Get user by ID"""
    result = get_user_by_id(id_user)
    if result:
        return jsonify(result)
    return jsonify({'error': 'User not found'}), 404

@app.route('/api/admin/users', methods=['POST'])
@admin_required
def api_create_user():
    """Create new user"""
    data = request.get_json()
    result = create_user(data)
    return jsonify(result)

@app.route('/api/admin/users/<id_user>', methods=['PUT'])
@admin_required
def api_update_user(id_user):
    """Update user"""
    data = request.get_json()
    result = update_user(id_user, data)
    return jsonify(result)

@app.route('/api/admin/users/<id_user>', methods=['DELETE'])
@admin_required
def api_delete_user(id_user):
    """Delete user"""
    result = delete_user(id_user)
    return jsonify(result)

@app.route('/api/admin/katalog', methods=['GET'])
@admin_required
def api_get_buku():
    """Get all books"""
    keyword = request.args.get('search')
    if keyword:
        buku_list = search_buku(keyword)
    else:
        buku_list = get_all_buku()
    return jsonify(buku_list)

@app.route('/api/admin/katalog/<id_buku>', methods=['GET'])
@admin_required
def api_get_buku_by_id(id_buku):
    """Get book by ID"""
    buku = get_buku_by_id(id_buku)
    if buku:
        return jsonify(buku)
    return jsonify({'error': 'Book not found'}), 404

@app.route('/api/admin/katalog', methods=['POST'])
@admin_required
def api_create_buku():
    """Create new book"""
    data = request.get_json()
    result = create_buku(
        data.get('judul'),
        data.get('penulis'),
        data.get('penerbit'),
        data.get('tahun_terbit'),
        data.get('isbn'),
        data.get('id_kategori'),
        data.get('deskripsi')
    )
    return jsonify(result)

@app.route('/api/admin/katalog/<id_buku>', methods=['PUT'])
@admin_required
def api_update_buku(id_buku):
    """Update book"""
    data = request.get_json()
    result = update_buku(
        id_buku,
        data.get('judul'),
        data.get('penulis'),
        data.get('penerbit'),
        data.get('tahun_terbit'),
        data.get('isbn'),
        data.get('id_kategori'),
        data.get('deskripsi')
    )
    return jsonify(result)

@app.route('/api/admin/katalog/<id_buku>', methods=['DELETE'])
@admin_required
def api_delete_buku(id_buku):
    """Delete book"""
    result = delete_buku(id_buku)
    return jsonify(result)

@app.route('/api/admin/kategori', methods=['GET'])
@admin_required
def api_get_kategori():
    """Get all categories"""
    result = get_all_kategori()
    return jsonify(result)

@app.route('/api/admin/kategori/<id_kategori>', methods=['GET'])
@admin_required
def api_get_kategori_by_id(id_kategori):
    """Get category by ID"""
    result = get_kategori_by_id(id_kategori)
    if result:
        return jsonify(result)
    return jsonify({'error': 'Category not found'}), 404

@app.route('/api/admin/kategori', methods=['POST'])
@admin_required
def api_create_kategori():
    """Create new category"""
    data = request.get_json()
    result = create_kategori(data)
    return jsonify(result)

@app.route('/api/admin/kategori/<id_kategori>', methods=['PUT'])
@admin_required
def api_update_kategori(id_kategori):
    """Update category"""
    data = request.get_json()
    result = update_kategori(id_kategori, data)
    return jsonify(result)

@app.route('/api/admin/kategori/<id_kategori>', methods=['DELETE'])
@admin_required
def api_delete_kategori(id_kategori):
    """Delete category"""
    result = delete_kategori(id_kategori)
    return jsonify(result)

@app.route('/api/admin/rak', methods=['GET'])
@admin_required
def api_get_rak():
    """Get all racks"""
    result = get_all_rak()
    return jsonify(result)

@app.route('/api/admin/rak/<id_rak>', methods=['GET'])
@admin_required
def api_get_rak_by_id(id_rak):
    """Get rack by ID"""
    result = get_rak_by_id(id_rak)
    if result:
        return jsonify(result)
    return jsonify({'error': 'Rack not found'}), 404

@app.route('/api/admin/rak', methods=['POST'])
@admin_required
def api_create_rak():
    """Create new rack"""
    data = request.get_json()
    result = create_rak(data)
    return jsonify(result)

@app.route('/api/admin/rak/<id_rak>', methods=['PUT'])
@admin_required
def api_update_rak(id_rak):
    """Update rack"""
    data = request.get_json()
    result = update_rak(id_rak, data)
    return jsonify(result)

@app.route('/api/admin/rak/<id_rak>', methods=['DELETE'])
@admin_required
def api_delete_rak(id_rak):
    """Delete rack"""
    result = delete_rak(id_rak)
    return jsonify(result)

# ==================== KARYAWAN ROUTES ====================

@app.route('/api/karyawan/dashboard/stats', methods=['GET'])
@karyawan_required
def karyawan_dashboard_stats():
    """Get karyawan dashboard statistics"""
    stats = karyawan_get_stats(session.get('user_id'))
    return jsonify(stats)

@app.route('/api/karyawan/peminjaman', methods=['POST'])
@karyawan_required
def api_proses_peminjaman():
    """Process book borrowing (only by staff)"""
    data = request.get_json()
    result = proses_peminjaman(
        data.get('id_peminjam'),
        data.get('barcode_list', []),
        session.get('user_id')
    )
    return jsonify(result)

@app.route('/api/karyawan/pengembalian', methods=['POST'])
@karyawan_required
def api_proses_pengembalian():
    """Process book return (only by staff)"""
    data = request.get_json()
    result = proses_pengembalian(
        data.get('id_pinjam'),
        session.get('user_id')
    )
    return jsonify(result)

@app.route('/api/karyawan/peminjaman/riwayat', methods=['GET'])
@karyawan_required
def api_get_riwayat_peminjaman():
    """Get borrowing history"""
    id_peminjam = request.args.get('id_peminjam')
    status = request.args.get('status')
    riwayat = get_riwayat_peminjaman(id_peminjam, status)
    return jsonify(riwayat)

@app.route('/api/karyawan/denda', methods=['GET'])
@karyawan_required
def api_get_denda():
    """Get all fines"""
    status = request.args.get('status')
    denda_list = get_all_denda(status)
    return jsonify(denda_list)

@app.route('/api/karyawan/denda/<id_denda>/bayar', methods=['POST'])
@karyawan_required
def api_bayar_denda(id_denda):
    """Pay fine"""
    result = bayar_denda(id_denda, session.get('user_id'))
    return jsonify(result)

@app.route('/api/karyawan/laporan/peminjaman', methods=['GET'])
@karyawan_required
def api_laporan_peminjaman():
    """Get borrowing report"""
    tgl_mulai = request.args.get('tgl_mulai')
    tgl_akhir = request.args.get('tgl_akhir')
    laporan = get_laporan_peminjaman(tgl_mulai, tgl_akhir)
    return jsonify(laporan)

@app.route('/api/karyawan/laporan/pengembalian', methods=['GET'])
@karyawan_required
def api_laporan_pengembalian():
    """Get return report"""
    tgl_mulai = request.args.get('tgl_mulai')
    tgl_akhir = request.args.get('tgl_akhir')
    laporan = get_laporan_pengembalian(tgl_mulai, tgl_akhir)
    return jsonify(laporan)

@app.route('/api/karyawan/laporan/statistik', methods=['GET'])
@karyawan_required
def api_statistik_bulanan():
    """Get monthly statistics"""
    bulan = request.args.get('bulan')
    tahun = request.args.get('tahun')
    stats = get_statistik_bulanan(int(bulan) if bulan else None, int(tahun) if tahun else None)
    return jsonify(stats)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
