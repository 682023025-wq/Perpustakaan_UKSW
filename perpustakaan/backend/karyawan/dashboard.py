from flask import Blueprint, render_template, jsonify
from config import get_db_connection
from backend.auth import login_required, check_role

karyawan_dashboard_bp = Blueprint('karyawan_dashboard', __name__)

@karyawan_dashboard_bp.route('/dashboard')
@login_required
@check_role(['PTGS'])
def dashboard():
    """Halaman dashboard karyawan dengan statistik"""
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        
        # Statistik untuk karyawan
        cursor.execute("SELECT COUNT(*) as total FROM PEMINJAMAN WHERE status_transaksi = 'Dipinjam'")
        sedang_dipinjam = cursor.fetchone()['total']
        
        cursor.execute("""
            SELECT COUNT(*) as total 
            FROM PEMINJAMAN p 
            WHERE p.status_transaksi = 'Dipinjam' AND p.tgl_jatuh_tempo < CURRENT_DATE
        """)
        terlambat = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM DENDA WHERE status_bayar = 'Belum Lunas'")
        denda_belum_lunas = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM ITEM_BUKU WHERE status_pinjam = 'Tersedia'")
        buku_tersedia = cursor.fetchone()['total']
        
        cursor.close()
        connection.close()
        
        stats = {
            'sedang_dipinjam': sedang_dipinjam,
            'terlambat': terlambat,
            'denda_belum_lunas': denda_belum_lunas,
            'buku_tersedia': buku_tersedia
        }
    else:
        stats = {'sedang_dipinjam': 0, 'terlambat': 0, 'denda_belum_lunas': 0, 'buku_tersedia': 0}
    
    return render_template('karyawan/dashboard.html', stats=stats)
