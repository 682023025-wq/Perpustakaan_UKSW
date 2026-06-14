"""
Modul Autentikasi untuk Sistem Perpustakaan
"""
from flask import session, jsonify, request
from functools import wraps
import mysql.connector
from config import DB_CONFIG

def get_db_connection():
    """Membuat koneksi ke database MySQL"""
    return mysql.connector.connect(**DB_CONFIG)

def login_user(username, password):
    """
    Fungsi login untuk user (admin/karyawan/user biasa)
    Returns: dict dengan status dan role user
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT id_user, username, nama, role 
        FROM USER 
        WHERE username = %s AND password = SHA2(%s, 256)
    """
    
    cursor.execute(query, (username, password))
    user = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if user:
        return {
            'success': True,
            'user': user
        }
    else:
        return {
            'success': False,
            'message': 'Username atau password salah'
        }

def login_required(f):
    """Decorator untuk memastikan user sudah login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Silakan login terlebih dahulu'}), 401
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator untuk memastikan user adalah admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Silakan login terlebih dahulu'}), 401
        if session.get('role') != 'ADMIN':
            return jsonify({'success': False, 'message': 'Akses ditolak. Hanya admin yang bisa mengakses'}), 403
        return f(*args, **kwargs)
    return decorated_function

def karyawan_required(f):
    """Decorator untuk memastikan user adalah karyawan"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Silakan login terlebih dahulu'}), 401
        if session.get('role') not in ['ADMIN', 'KARYAWAN']:
            return jsonify({'success': False, 'message': 'Akses ditolak. Hanya petugas yang bisa mengakses'}), 403
        return f(*args, **kwargs)
    return decorated_function

def logout_user():
    """Logout user dengan menghapus session"""
    session.clear()
    return {'success': True, 'message': 'Berhasil logout'}
