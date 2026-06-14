from flask import Blueprint, render_template, request, jsonify, session
from config import get_db_connection
from backend.auth import login_required, check_role
from datetime import datetime, timedelta
import logging

# Setup logging untuk mencatat error di server tanpa menampilkannya ke user
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

pengembalian_bp = Blueprint('pengembalian', __name__)

@pengembalian_bp.route('/')
@login_required
@check_role(['PTGS'])
def index():
    return render_template('karyawan/pengembalian.html')

@pengembalian_bp.route('/api/pengembalian', methods=['GET'])
@login_required
@check_role(['PTGS'])
def get_pengembalian():
    """Mengambil riwayat pengembalian buku (misal: hari ini)"""
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        try:
            query = """
                SELECT p.id_pinjam, u.nama_lengkap as nama_peminjam, k.judul, 
                       p.tgl_kembali, d.nominal_denda, d.status_bayar,
                       CASE 
                           WHEN d.nominal_denda > 0 THEN 'Ada Denda'
                           ELSE 'Lunas / Tidak Ada Denda'
                       END as status_denda
                FROM PEMINJAMAN p
                JOIN USERS u ON p.id_peminjam = u.id_user
                JOIN ITEM_BUKU i ON p.id_barcode = i.id_barcode
                JOIN KATALOG_BUKU k ON i.isbn = k.isbn
                LEFT JOIN DENDA d ON p.id_pinjam = d.id_pinjam
                WHERE p.status_transaksi = 'Selesai' AND p.tgl_kembali = CURRENT_DATE
                ORDER BY p.tgl_kembali DESC, p.id_pinjam DESC
            """
            cursor.execute(query)
            pengembalian = cursor.fetchall()
            
            # Konversi objek date ke string agar aman di-serialize ke JSON
            for row in pengembalian:
                if row['tgl_kembali']:
                    row['tgl_kembali'] = row['tgl_kembali'].strftime('%Y-%m-%d')
                # Pastikan nominal_denda tidak None
                if row['nominal_denda'] is None:
                    row['nominal_denda'] = 0.00
                    
            return jsonify(pengembalian), 200
            
        except Exception as e:
            logger.error(f"Error fetching pengembalian: {e}")
            return jsonify({'success': False, 'error': 'Gagal memuat riwayat pengembalian'}), 500
        finally:
            cursor.close()
            connection.close()
            
    return jsonify({'success': False, 'error': 'Koneksi database gagal'}), 500

@pengembalian_bp.route('/api/pengembalian/proses', methods=['POST'])
@login_required
@check_role(['PTGS'])
def proses_pengembalian():
    """Petugas menerima pengembalian buku dan menghitung denda jika terlambat"""
    data = request.json
    if not data:
        return jsonify({'success': False, 'error': 'Data tidak valid'}), 400

    # Sanitasi input
    id_pinjam = str(data.get('id_pinjam', '')).strip()
    id_petugas = session.get('user_id')

    if not id_pinjam:
        return jsonify({'success': False, 'error': 'ID Peminjaman wajib diisi'}), 400

    connection = get_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        try:
            # 1. Ambil data peminjaman yang masih aktif (status 'Dipinjam')
            cursor.execute("""
                SELECT p.id_pinjam, p.id_barcode, p.tgl_jatuh_tempo, p.status_transaksi,
                       i.isbn
                FROM PEMINJAMAN p
                JOIN ITEM_BUKU i ON p.id_barcode = i.id_barcode
                WHERE p.id_pinjam = %s AND p.status_transaksi = 'Dipinjam'
            """, (id_pinjam,))
            pinjam = cursor.fetchone()
            
            if not pinjam:
                return jsonify({'success': False, 'error': 'ID Peminjaman tidak ditemukan atau buku sudah dikembalikan'}), 404
            
            # 2. Hitung keterlambatan dan denda (Asumsi: Rp 2.000 per hari)
            tgl_kembali = datetime.now().date()
            tgl_jatuh_tempo = pinjam['tgl_jatuh_tempo']
            nominal_denda = 0
            
            if isinstance(tgl_jatuh_tempo, str):
                tgl_jatuh_tempo = datetime.strptime(tgl_jatuh_tempo, '%Y-%m-%d').date()
                
            if tgl_kembali > tgl_jatuh_tempo:
                hari_terlambat = (tgl_kembali - tgl_jatuh_tempo).days
                nominal_denda = hari_terlambat * 2000
            
            # 3. Update status peminjaman menjadi 'Selesai'
            cursor.execute("""
                UPDATE PEMINJAMAN 
                SET tgl_kembali = %s, id_petugas_in = %s, status_transaksi = 'Selesai'
                WHERE id_pinjam = %s
            """, (tgl_kembali, id_petugas, id_pinjam))
            
            # 4. Update status item buku menjadi 'Tersedia'
            cursor.execute("""
                UPDATE ITEM_BUKU 
                SET status_pinjam = 'Tersedia' 
                WHERE id_barcode = %s
            """, (pinjam['id_barcode'],))
            
            # 5. Buat record denda jika ada keterlambatan
            if nominal_denda > 0:
                cursor.execute("SELECT COUNT(*) as total FROM DENDA")
                no_urut = cursor.fetchone()['total'] + 1
                tahun = datetime.now().year
                id_denda = f'D-{tahun}-{no_urut:03d}'
                
                cursor.execute("""
                    INSERT INTO DENDA (id_denda, id_pinjam, nominal_denda, status_bayar)
                    VALUES (%s, %s, %s, 'Belum Lunas')
                """, (id_denda, id_pinjam, nominal_denda))
            
            # Commit semua perubahan transaksi
            connection.commit()
            
            response_data = {
                'success': True,
                'message': 'Pengembalian berhasil diproses',
                'tgl_kembali': tgl_kembali.strftime('%Y-%m-%d'),
                'denda': nominal_denda
            }
            
            if nominal_denda > 0:
                response_data['message'] += f'. Terdapat denda keterlambatan sebesar Rp {nominal_denda:,}.'
                
            return jsonify(response_data), 200
            
        except Exception as e:
            connection.rollback() # Batalkan transaksi jika ada error
            logger.error(f"Error proses pengembalian: {e}")
            return jsonify({'success': False, 'error': 'Terjadi kesalahan internal server. Silakan coba lagi.'}), 500
        finally:
            cursor.close()
            connection.close()
            
    return jsonify({'success': False, 'error': 'Koneksi database gagal'}), 500