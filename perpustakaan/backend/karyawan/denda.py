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

@denda_bp.route('/api/pengembalian/proses', methods=['POST'])
@login_required
@check_role(['PTGS'])
def proses_pengembalian():
    """Petugas menerima pengembalian buku"""
    data = request.json
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        try:
            id_pinjam = data['id_pinjam']
            id_petugas = session.get('user_id')
            
            # Get info peminjaman
            cursor.execute("""
                SELECT p.*, i.isbn 
                FROM PEMINJAMAN p
                JOIN ITEM_BUKU i ON p.id_barcode = i.id_barcode
                WHERE p.id_pinjam = %s AND p.status_transaksi = 'Dipinjam'
            """, (id_pinjam,))
            pinjam = cursor.fetchone()
            
            if not pinjam:
                return jsonify({'success': False, 'error': 'Peminjaman tidak ditemukan'}), 400
            
            tgl_kembali = datetime.now().date()
            tgl_jatuh_tempo = pinjam['tgl_jatuh_tempo']
            
            # Hitung denda jika terlambat (asumsi Rp 2000/hari)
            nominal_denda = 0
            if tgl_kembali > tgl_jatuh_tempo:
                hari_terlambat = (tgl_kembali - tgl_jatuh_tempo).days
                nominal_denda = hari_terlambat * 2000
            
            # Update peminjaman
            cursor.execute("""
                UPDATE PEMINJAMAN 
                SET tgl_kembali = %s, id_petugas_in = %s, status_transaksi = 'Selesai'
                WHERE id_pinjam = %s
            """, (tgl_kembali, id_petugas, id_pinjam))
            
            # Update status item buku
            cursor.execute("UPDATE ITEM_BUKU SET status_pinjam = 'Tersedia' WHERE id_barcode = %s", (pinjam['id_barcode'],))
            
            # Buat denda jika ada
            if nominal_denda > 0:
                cursor.execute("SELECT COUNT(*) as total FROM DENDA")
                no_urut = cursor.fetchone()['total'] + 1
                tahun = datetime.now().year
                id_denda = f'D-{tahun}-{no_urut:03d}'
                
                cursor.execute("""
                    INSERT INTO DENDA (id_denda, id_pinjam, nominal_denda, status_bayar)
                    VALUES (%s, %s, %s, 'Belum Lunas')
                """, (id_denda, id_pinjam, nominal_denda))
            
            connection.commit()
            return jsonify({
                'success': True,
                'denda': nominal_denda,
                'tgl_kembali': str(tgl_kembali)
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400
        finally:
            cursor.close()
            connection.close()
    return jsonify({'success': False}), 500

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
