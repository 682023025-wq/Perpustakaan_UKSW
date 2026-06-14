"""
Manajemen Peminjaman Buku - Hanya bisa dilakukan oleh petugas/karyawan
"""
import mysql.connector
from config import DB_CONFIG
from datetime import timedelta, date

def get_db_connection():
    """Membuat koneksi ke database MySQL"""
    return mysql.connector.connect(**DB_CONFIG)

def proses_peminjaman(id_peminjam, barcode_list, id_petugas_out):
    """
    Petugas meminjamkan buku atas nama user/peminjam
    Parameter:
        - id_peminjam: ID user yang meminjam
        - barcode_list: List barcode buku yang dipinjam
        - id_petugas_out: ID petugas yang memproses peminjaman
    Returns: dict dengan status dan detail peminjaman
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # 1. Cek apakah peminjam ada dan aktif
        cursor.execute("""
            SELECT u.id_user, u.nama_lengkap, r.nama_role as role, r.max_kuota, u.status_aktif
            FROM USERS u
            JOIN ROLES r ON u.id_role = r.id_role
            WHERE u.id_user = %s AND u.status_aktif = 'Aktif'
        """, (id_peminjam,))
        peminjam = cursor.fetchone()
        
        if not peminjam:
            return {'success': False, 'message': 'Peminjam tidak ditemukan atau tidak aktif'}
        
        # 2. Cek kuota peminjaman berdasarkan role
        cursor.execute("""
            SELECT COUNT(*) as jumlah 
            FROM PEMINJAMAN 
            WHERE id_peminjam = %s AND status_transaksi = 'Dipinjam'
        """, (id_peminjam,))
        jumlah_pinjam_aktif = cursor.fetchone()['jumlah']
        
        max_kuota = peminjam['max_kuota']
        if jumlah_pinjam_aktif + len(barcode_list) > max_kuota:
            return {'success': False, 'message': f'Kuota peminjaman terlampaui. Maksimal {max_kuota} buku.'}
        
        # 3. Cek apakah ada denda belum lunas
        cursor.execute("""
            SELECT SUM(nominal_denda) as total_denda 
            FROM DENDA d
            JOIN PEMINJAMAN p ON d.id_pinjam = p.id_pinjam
            WHERE p.id_peminjam = %s AND d.status_bayar = 'Belum Lunas'
        """, (id_peminjam,))
        result = cursor.fetchone()
        total_denda = result['total_denda'] or 0
        
        if total_denda > 0:
            return {'success': False, 'message': f'Masih ada denda belum lunas: Rp {total_denda:,}'}
        
        # 4. Validasi setiap barcode buku
        items_valid = []
        for barcode in barcode_list:
            cursor.execute("""
                SELECT ib.id_barcode, ib.isbn, ib.status_pinjam, k.judul
                FROM ITEM_BUKU ib
                JOIN KATALOG_BUKU k ON ib.isbn = k.isbn
                WHERE ib.id_barcode = %s
            """, (barcode,))
            item = cursor.fetchone()
            
            if not item:
                return {'success': False, 'message': f'Barcode {barcode} tidak ditemukan'}
            
            if item['status_pinjam'] != 'Tersedia':
                return {'success': False, 'message': f'Buku "{item["judul"]}" sedang tidak tersedia'}
            
            items_valid.append(item)
        
        # 5. Buat record PEMINJAMAN untuk setiap buku
        tgl_pinjam = date.today()
        
        # Dapatkan durasi pinjam dari role
        cursor.execute("SELECT durasi_pinjam FROM ROLES WHERE id_role = %s", (peminjam['role'],))
        durasi = cursor.fetchone()['durasi_pinjam']
        tgl_jatuh_tempo = tgl_pinjam + timedelta(days=durasi)
        
        hasil_pinjam = []
        for item in items_valid:
            # Generate ID pinjam unik
            cursor.execute("SELECT CONCAT('P-', DATE_FORMAT(NOW(), '%Y'), '-', LPAD(COALESCE(MAX(CAST(SUBSTRING_INDEX(id_pinjam, '-', -1) AS UNSIGNED)), 0) + 1, 3, '0')) as new_id FROM PEMINJAMAN WHERE id_pinjam LIKE CONCAT('P-', YEAR(NOW()), '-%')")
            id_pinjam_result = cursor.fetchone()
            id_pinjam = id_pinjam_result['new_id']
            
            cursor.execute("""
                INSERT INTO PEMINJAMAN (id_pinjam, id_peminjam, id_barcode, tgl_pinjam, tgl_jatuh_tempo, id_petugas_out, status_transaksi)
                VALUES (%s, %s, %s, %s, %s, %s, 'Dipinjam')
            """, (id_pinjam, id_peminjam, item['id_barcode'], tgl_pinjam, tgl_jatuh_tempo, id_petugas_out))
            
            # Update status ITEM_BUKU
            cursor.execute("""
                UPDATE ITEM_BUKU 
                SET status_pinjam = 'Dipinjam'
                WHERE id_barcode = %s
            """, (item['id_barcode'],))
            
            hasil_pinjam.append({
                'id_pinjam': id_pinjam,
                'barcode': item['id_barcode'],
                'judul': item['judul']
            })
        
        conn.commit()
        
        return {
            'success': True, 
            'message': f'Peminjaman berhasil diproses ({len(items_valid)} buku)',
            'detail': hasil_pinjam,
            'tgl_kembali_wajib': tgl_jatuh_tempo.strftime('%d-%m-%Y'),
            'jumlah_buku': len(items_valid)
        }
        
    except mysql.connector.Error as err:
        conn.rollback()
        return {'success': False, 'message': f'Error: {str(err)}'}
    finally:
        cursor.close()
        conn.close()

def proses_pengembalian(id_pinjam, id_petugas_in):
    """
    Petugas menerima pengembalian buku
    Parameter:
        - id_pinjam: ID peminjaman
        - id_petugas_in: ID petugas yang menerima pengembalian
    Returns: dict dengan status dan detail pengembalian
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # 1. Cek apakah peminjaman ada
        cursor.execute("""
            SELECT p.*, u.nama_lengkap as peminjam
            FROM PEMINJAMAN p
            JOIN USERS u ON p.id_peminjam = u.id_user
            WHERE p.id_pinjam = %s
        """, (id_pinjam,))
        peminjaman = cursor.fetchone()
        
        if not peminjaman:
            return {'success': False, 'message': 'ID peminjaman tidak ditemukan'}
        
        if peminjaman['status_transaksi'] != 'Dipinjam':
            return {'success': False, 'message': 'Status peminjaman bukan "Dipinjam"'}
        
        # 2. Hitung denda jika terlambat
        tgl_kembali = date.today()
        tgl_kembali_wajib = peminjaman['tgl_jatuh_tempo']
        denda = 0
        
        if tgl_kembali > tgl_kembali_wajib:
            hari_terlambat = (tgl_kembali - tgl_kembali_wajib).days
            denda = hari_terlambat * 1000  # Rp 1000 per hari
        
        # 3. Update PEMINJAMAN
        cursor.execute("""
            UPDATE PEMINJAMAN 
            SET tgl_kembali = %s, id_petugas_in = %s, status_transaksi = 'Selesai'
            WHERE id_pinjam = %s
        """, (tgl_kembali, id_petugas_in, id_pinjam))
        
        # 4. Update status ITEM_BUKU menjadi Tersedia
        cursor.execute("""
            UPDATE ITEM_BUKU 
            SET status_pinjam = 'Tersedia'
            WHERE id_barcode IN (SELECT id_barcode FROM PEMINJAMAN WHERE id_pinjam = %s)
        """, (id_pinjam,))
        
        # 5. Jika ada denda, buat record DENDA
        if denda > 0:
            # Generate ID denda unik
            cursor.execute("SELECT CONCAT('D-', DATE_FORMAT(NOW(), '%Y'), '-', LPAD(COALESCE(MAX(CAST(SUBSTRING_INDEX(id_denda, '-', -1) AS UNSIGNED)), 0) + 1, 3, '0')) as new_id FROM DENDA WHERE id_denda LIKE CONCAT('D-', YEAR(NOW()), '-%')")
            id_denda_result = cursor.fetchone()
            id_denda = id_denda_result['new_id']
            
            cursor.execute("""
                INSERT INTO DENDA (id_denda, id_pinjam, nominal_denda, status_bayar)
                VALUES (%s, %s, %s, 'Belum Lunas')
            """, (id_denda, id_pinjam, denda))
        
        conn.commit()
        
        result = {
            'success': True,
            'message': 'Pengembalian berhasil diproses',
            'tgl_kembali': tgl_kembali.strftime('%d-%m-%Y'),
            'denda': denda
        }
        
        if denda > 0:
            result['message'] += f'. Terdapat denda: Rp {denda:,}'
        
        return result
        
    except mysql.connector.Error as err:
        conn.rollback()
        return {'success': False, 'message': f'Error: {str(err)}'}
    finally:
        cursor.close()
        conn.close()

def get_detail_peminjaman(id_pinjam):
    """Mengambil detail peminjaman"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT p.id_pinjam, u.nama_lengkap as peminjam,
               p.tgl_pinjam, p.tgl_jatuh_tempo, p.tgl_kembali,
               p.status_transaksi, pt_out.nama_lengkap as petugas_out, pt_in.nama_lengkap as petugas_in,
               k.judul, p.id_barcode
        FROM PEMINJAMAN p
        JOIN USERS u ON p.id_peminjam = u.id_user
        LEFT JOIN USERS pt_out ON p.id_petugas_out = pt_out.id_user
        LEFT JOIN USERS pt_in ON p.id_petugas_in = pt_in.id_user
        JOIN KATALOG_BUKU k ON p.id_barcode = k.isbn
        WHERE p.id_pinjam = %s
    """, (id_pinjam,))
    
    detail = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return detail

def get_riwayat_peminjaman(id_peminjam=None, status=None):
    """Mengambil riwayat peminjaman dengan filter opsional"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT DISTINCT p.id_pinjam, u.nama_lengkap as peminjam,
               p.tgl_pinjam, p.tgl_jatuh_tempo, p.tgl_kembali,
               p.status_transaksi, pt_out.nama_lengkap as petugas_out
        FROM PEMINJAMAN p
        JOIN USERS u ON p.id_peminjam = u.id_user
        LEFT JOIN USERS pt_out ON p.id_petugas_out = pt_out.id_user
        WHERE 1=1
    """
    
    params = []
    
    if id_peminjam:
        query += " AND p.id_peminjam = %s"
        params.append(id_peminjam)
    
    if status:
        query += " AND p.status_transaksi = %s"
        params.append(status)
    
    query += " ORDER BY p.tgl_pinjam DESC"
    
    cursor.execute(query, params)
    hasil = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return hasil
