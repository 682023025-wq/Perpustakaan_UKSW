from flask import Blueprint, render_template, request, jsonify, session
from config import get_db_connection
from backend.auth import login_required, check_role
from datetime import datetime, timedelta

peminjaman_bp = Blueprint('peminjaman', __name__)

@peminjaman_bp.route('/')
@login_required
@check_role(['PTGS'])
def index():
    return render_template('karyawan/peminjaman.html')

@peminjaman_bp.route('/api/peminjaman', methods=['GET'])
@login_required
@check_role(['PTGS'])
def get_peminjaman():
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT p.*, u.nama_lengkap as nama_peminjam, k.judul, i.isbn,
                   po.nama_lengkap as petugas_out
            FROM PEMINJAMAN p
            JOIN USERS u ON p.id_peminjam = u.id_user
            JOIN ITEM_BUKU i ON p.id_barcode = i.id_barcode
            JOIN KATALOG_BUKU k ON i.isbn = k.isbn
            JOIN USERS po ON p.id_petugas_out = po.id_user
            WHERE p.status_transaksi = 'Dipinjam'
            ORDER BY p.tgl_jatuh_tempo ASC
        """
        cursor.execute(query)
        peminjaman = cursor.fetchall()
        cursor.close()
        connection.close()
        return jsonify(peminjaman)
    return jsonify([]), 500

@peminjaman_bp.route('/api/peminjaman/proses', methods=['POST'])
@login_required
@check_role(['PTGS'])
def proses_peminjaman():
    """Petugas meminjamkan buku atas nama user"""
    data = request.json
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        try:
            id_peminjam = data['id_peminjam']
            id_barcode = data['id_barcode']
            id_petugas = session.get('user_id')
            
            # 1. Cek status user
            cursor.execute("SELECT * FROM USERS WHERE id_user = %s AND status_aktif = 'Aktif'", (id_peminjam,))
            user = cursor.fetchone()
            if not user:
                return jsonify({'success': False, 'error': 'User tidak ditemukan atau nonaktif'}), 400
            
            # 2. Cek role user untuk kuota
            cursor.execute("""
                SELECT r.max_kuota, r.durasi_pinjam 
                FROM ROLES r 
                JOIN USERS u ON r.id_role = u.id_role 
                WHERE u.id_user = %s
            """, (id_peminjam,))
            role_info = cursor.fetchone()
            
            if role_info['max_kuota'] == 0:
                return jsonify({'success': False, 'error': 'User ini tidak memiliki hak pinjam'}), 400
            
            # 3. Cek jumlah pinjaman aktif user
            cursor.execute("""
                SELECT COUNT(*) as jumlah 
                FROM PEMINJAMAN 
                WHERE id_peminjam = %s AND status_transaksi = 'Dipinjam'
            """, (id_peminjam,))
            jumlah_pinjam = cursor.fetchone()['jumlah']
            
            if jumlah_pinjam >= role_info['max_kuota']:
                return jsonify({'success': False, 'error': f'Kuota pinjaman penuh (max {role_info["max_kuota"]})'}), 400
            
            # 4. Cek status buku
            cursor.execute("SELECT * FROM ITEM_BUKU WHERE id_barcode = %s", (id_barcode,))
            item = cursor.fetchone()
            if not item or item['status_pinjam'] != 'Tersedia':
                return jsonify({'success': False, 'error': 'Buku tidak tersedia'}), 400
            
            # 5. Cek denda belum lunas
            cursor.execute("""
                SELECT COUNT(*) as total 
                FROM DENDA d 
                JOIN PEMINJAMAN p ON d.id_pinjam = p.id_pinjam 
                WHERE p.id_peminjam = %s AND d.status_bayar = 'Belum Lunas'
            """, (id_peminjam,))
            denda_count = cursor.fetchone()['total']
            
            if denda_count > 0:
                return jsonify({'success': False, 'error': 'User masih memiliki denda yang belum lunas'}), 400
            
            # 6. Buat ID peminjaman
            tahun = datetime.now().year
            cursor.execute("SELECT COUNT(*) as total FROM PEMINJAMAN WHERE id_pinjam LIKE %s", (f'P-{tahun}-%',))
            no_urut = cursor.fetchone()['total'] + 1
            id_pinjam = f'P-{tahun}-{no_urut:03d}'
            
            # 7. Hitung tanggal jatuh tempo
            tgl_pinjam = datetime.now()
            tgl_jatuh_tempo = tgl_pinjam + timedelta(days=role_info['durasi_pinjam'])
            
            # 8. Insert peminjaman
            query = """
                INSERT INTO PEMINJAMAN 
                (id_pinjam, id_peminjam, id_barcode, tgl_pinjam, tgl_jatuh_tempo, 
                 jumlah_extend, id_petugas_out, status_transaksi)
                VALUES (%s, %s, %s, %s, %s, 0, %s, 'Dipinjam')
            """
            cursor.execute(query, (
                id_pinjam, id_peminjam, id_barcode,
                tgl_pinjam.date(), tgl_jatuh_tempo.date(),
                id_petugas
            ))
            
            # 9. Update status item buku
            cursor.execute("UPDATE ITEM_BUKU SET status_pinjam = 'Dipinjam' WHERE id_barcode = %s", (id_barcode,))
            
            connection.commit()
            return jsonify({'success': True, 'id_pinjam': id_pinjam}), 201
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400
        finally:
            cursor.close()
            connection.close()
    return jsonify({'success': False}), 500

@peminjaman_bp.route('/api/peminjaman/<id_pinjam>/extend', methods=['POST'])
@login_required
@check_role(['PTGS'])
def extend_peminjaman(id_pinjam):
    """Extend masa pinjam"""
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        try:
            # Get info peminjaman
            cursor.execute("""
                SELECT p.*, r.max_extend, r.durasi_pinjam
                FROM PEMINJAMAN p
                JOIN USERS u ON p.id_peminjam = u.id_user
                JOIN ROLES r ON u.id_role = r.id_role
                WHERE p.id_pinjam = %s
            """, (id_pinjam,))
            pinjam = cursor.fetchone()
            
            if not pinjam:
                return jsonify({'success': False, 'error': 'Peminjaman tidak ditemukan'}), 400
            
            if pinjam['jumlah_extend'] >= pinjam['max_extend']:
                return jsonify({'success': False, 'error': 'Maksimal extend telah tercapai'}), 400
            
            # Update tanggal jatuh tempo dan jumlah extend
            new_jatuh_tempo = datetime.strptime(str(pinjam['tgl_jatuh_tempo']), '%Y-%m-%d') + timedelta(days=pinjam['durasi_pinjam'])
            
            cursor.execute("""
                UPDATE PEMINJAMAN 
                SET tgl_jatuh_tempo = %s, jumlah_extend = jumlah_extend + 1
                WHERE id_pinjam = %s
            """, (new_jatuh_tempo.date(), id_pinjam))
            
            connection.commit()
            return jsonify({'success': True, 'new_jatuh_tempo': str(new_jatuh_tempo.date())})
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400
        finally:
            cursor.close()
            connection.close()
    return jsonify({'success': False}), 500
