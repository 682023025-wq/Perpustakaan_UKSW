from flask import Blueprint, render_template, jsonify
from config import get_db_connection
from backend.auth import login_required, check_role

admin_dashboard_bp = Blueprint('admin_dashboard', __name__)

@admin_dashboard_bp.route('/dashboard')
@login_required
@check_role(['SPRADM'])
def dashboard():
    """Halaman dashboard admin dengan statistik"""
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        
        # Statistik umum
        cursor.execute("SELECT COUNT(*) as total FROM USERS WHERE status_aktif = 'Aktif'")
        total_users = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM KATALOG_BUKU")
        total_buku = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM PEMINJAMAN WHERE status_transaksi = 'Dipinjam'")
        sedang_dipinjam = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM DENDA WHERE status_bayar = 'Belum Lunas'")
        denda_belum_lunas = cursor.fetchone()['total']
        
        cursor.close()
        connection.close()
        
        stats = {
            'total_users': total_users,
            'total_buku': total_buku,
            'sedang_dipinjam': sedang_dipinjam,
            'denda_belum_lunas': denda_belum_lunas
        }
    else:
        stats = {'total_users': 0, 'total_buku': 0, 'sedang_dipinjam': 0, 'denda_belum_lunas': 0}
    
    return render_template('admin/dashboard.html', stats=stats)
