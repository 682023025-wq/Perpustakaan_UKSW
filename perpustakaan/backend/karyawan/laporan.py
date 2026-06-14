from flask import Blueprint, render_template, request, jsonify
from config import get_db_connection
from backend.auth import login_required, check_role

laporan_bp = Blueprint('laporan', __name__)

@laporan_bp.route('/')
@login_required
@check_role(['PTGS'])
def index():
    return render_template('karyawan/laporan.html')

@laporan_bp.route('/api/laporan/peminjaman', methods=['GET'])
@login_required
@check_role(['PTGS'])
def laporan_peminjaman():
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT p.*, u.nama_lengkap as nama_peminjam, k.judul, i.isbn,
                   po.nama_lengkap as petugas_out, pi.nama_lengkap as petugas_in
            FROM PEMINJAMAN p
            JOIN USERS u ON p.id_peminjam = u.id_user
            JOIN ITEM_BUKU i ON p.id_barcode = i.id_barcode
            JOIN KATALOG_BUKU k ON i.isbn = k.isbn
            JOIN USERS po ON p.id_petugas_out = po.id_user
            LEFT JOIN USERS pi ON p.id_petugas_in = pi.id_user
            ORDER BY p.created_at DESC
            LIMIT 100
        """
        cursor.execute(query)
        laporan = cursor.fetchall()
        cursor.close()
        connection.close()
        return jsonify(laporan)
    return jsonify([]), 500

@laporan_bp.route('/api/laporan/statistik', methods=['GET'])
@login_required
@check_role(['PTGS'])
def laporan_statistik():
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        
        # Total peminjaman per bulan
        cursor.execute("""
            SELECT DATE_FORMAT(tgl_pinjam, '%Y-%m') as bulan, COUNT(*) as total
            FROM PEMINJAMAN
            GROUP BY DATE_FORMAT(tgl_pinjam, '%Y-%m')
            ORDER BY bulan DESC
            LIMIT 6
        """)
        peminjaman_per_bulan = cursor.fetchall()
        
        # Buku paling sering dipinjam
        cursor.execute("""
            SELECT k.judul, COUNT(*) as total_pinjam
            FROM PEMINJAMAN p
            JOIN ITEM_BUKU i ON p.id_barcode = i.id_barcode
            JOIN KATALOG_BUKU k ON i.isbn = k.isbn
            GROUP BY k.judul
            ORDER BY total_pinjam DESC
            LIMIT 5
        """)
        buku_populer = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'peminjaman_per_bulan': peminjaman_per_bulan,
            'buku_populer': buku_populer
        })
    return jsonify({}), 500
