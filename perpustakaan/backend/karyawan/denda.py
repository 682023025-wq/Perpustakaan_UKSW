from flask import Blueprint, render_template, request, jsonify, session
from config import get_db_connection
from backend.auth import login_required, check_role
from datetime import datetime

denda_bp = Blueprint('denda', __name__)

@denda_bp.route('/')
@login_required
@check_role(['PTGS'])
def index():
    return render_template('karyawan/denda.html')

@denda_bp.route('/api/denda', methods=['GET'])
@login_required
@check_role(['PTGS'])
def get_denda():
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT d.*, p.id_pinjam, u.nama_lengkap as nama_peminjam,
                   p.tgl_jatuh_tempo, p.tgl_kembali
            FROM DENDA d
            JOIN PEMINJAMAN p ON d.id_pinjam = p.id_pinjam
            JOIN USERS u ON p.id_peminjam = u.id_user
            ORDER BY d.created_at DESC
        """
        cursor.execute(query)
        denda = cursor.fetchall()
        cursor.close()
        connection.close()
        return jsonify(denda)
    return jsonify([]), 500


@denda_bp.route('/api/denda/<id_denda>/bayar', methods=['POST'])
@login_required
@check_role(['PTGS'])
def bayar_denda(id_denda):
    """Proses pembayaran denda"""
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("""
                UPDATE DENDA 
                SET status_bayar = 'Lunas', tgl_bayar = CURRENT_DATE
                WHERE id_denda = %s
            """, (id_denda,))
            connection.commit()
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400
        finally:
            cursor.close()
            connection.close()
    return jsonify({'success': False}), 500
