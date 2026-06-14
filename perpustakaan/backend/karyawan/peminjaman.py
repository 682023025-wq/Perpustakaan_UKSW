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
            SELECT id_user, nama, role, status 
            FROM USER 
            WHERE id_user = %s AND status = 'Aktif'
        """, (id_peminjam,))
        peminjam = cursor.fetchone()
        
        if not peminjam:
            return {'success': False, 'message': 'Peminjam tidak ditemukan atau tidak aktif'}
        
        # 2. Cek kuota peminjaman (max 5 buku untuk MHS/DSN)
        cursor.execute("""
            SELECT COUNT(*) as jumlah 
            FROM PEMINJAMAN 
            WHERE id_peminjam = %s AND status = 'Dipinjam'
        """, (id_peminjam,))
        jumlah_pinjam_aktif = cursor.fetchone()['jumlah']
        
        if jumlah_pinjam_aktif + len(barcode_list) > 5:
            return {'success': False, 'message': f'Kuota peminjaman terlampaui. Sisa kuota: {5 - jumlah_pinjam_aktif}'}
        
        # 3. Cek apakah ada denda belum lunas
        cursor.execute("""
            SELECT SUM(jumlah_denda) as total_denda 
            FROM DENDA 
            WHERE id_pinjam IN (
                SELECT id_pinjam FROM PEMINJAMAN WHERE id_peminjam = %s
            ) AND status = 'Belum Lunas'
        """, (id_peminjam,))
        result = cursor.fetchone()
        total_denda = result['total_denda'] or 0
        
        if total_denda > 0:
            return {'success': False, 'message': f'Masih ada denda belum lunas: Rp {total_denda:,}'}
        
        # 4. Validasi setiap barcode buku
        items_valid = []
        for barcode in barcode_list:
            cursor.execute("""
                SELECT ib.id_item, ib.id_buku, ib.status, b.judul
                FROM ITEM_BUKU ib
                JOIN BUKU b ON ib.id_buku = b.id_buku
                WHERE ib.barcode = %s
            """, (barcode,))
            item = cursor.fetchone()
            
            if not item:
                return {'success': False, 'message': f'Barcode {barcode} tidak ditemukan'}
            
            if item['status'] != 'Tersedia':
                return {'success': False, 'message': f'Buku "{item["judul"]}" sedang tidak tersedia'}
            
            items_valid.append(item)
        
        # 5. Buat record PEMINJAMAN
        tgl_pinjam = date.today()
        tgl_kembali_wajib = tgl_pinjam + timedelta(days=7)  # 7 hari pinjaman
        
        cursor.execute("""
            INSERT INTO PEMINJAMAN (id_peminjam, id_petugas_out, tgl_pinjam, tgl_kembali_wajib, status)
            VALUES (%s, %s, %s, %s, 'Dipinjam')
        """, (id_peminjam, id_petugas_out, tgl_pinjam, tgl_kembali_wajib))
        
        id_pinjam = cursor.lastrowid
        
        # 6. Buat DETAIL_PINJAM dan update status ITEM_BUKU
        for item in items_valid:
            cursor.execute("""
                INSERT INTO DETAIL_PINJAM (id_pinjam, id_item)
                VALUES (%s, %s)
            """, (id_pinjam, item['id_item']))
            
            cursor.execute("""
                UPDATE ITEM_BUKU 
                SET status = 'Dipinjam'
                WHERE id_item = %s
            """, (item['id_item'],))
        
        conn.commit()
        
        return {
            'success': True, 
            'message': 'Peminjaman berhasil diproses',
            'id_pinjam': id_pinjam,
            'tgl_kembali_wajib': tgl_kembali_wajib.strftime('%d-%m-%Y'),
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
            SELECT p.*, u.nama as peminjam
            FROM PEMINJAMAN p
            JOIN USER u ON p.id_peminjam = u.id_user
            WHERE p.id_pinjam = %s
        """, (id_pinjam,))
        peminjaman = cursor.fetchone()
        
        if not peminjaman:
            return {'success': False, 'message': 'ID peminjaman tidak ditemukan'}
        
        if peminjaman['status'] != 'Dipinjam':
            return {'success': False, 'message': 'Status peminjaman bukan "Dipinjam"'}
        
        # 2. Hitung denda jika terlambat
        tgl_kembali = date.today()
        tgl_kembali_wajib = peminjaman['tgl_kembali_wajib']
        denda = 0
        
        if tgl_kembali > tgl_kembali_wajib:
            hari_terlambat = (tgl_kembali - tgl_kembali_wajib).days
            denda = hari_terlambat * 1000  # Rp 1000 per hari
        
        # 3. Update PEMINJAMAN
        cursor.execute("""
            UPDATE PEMINJAMAN 
            SET tgl_kembali = %s, id_petugas_in = %s, status = 'Dikembalikan'
            WHERE id_pinjam = %s
        """, (tgl_kembali, id_petugas_in, id_pinjam))
        
        # 4. Update status ITEM_BUKU menjadi Tersedia
        cursor.execute("""
            UPDATE ITEM_BUKU ib
            JOIN DETAIL_PINJAM dp ON ib.id_item = dp.id_item
            SET ib.status = 'Tersedia'
            WHERE dp.id_pinjam = %s
        """, (id_pinjam,))
        
        # 5. Jika ada denda, buat record DENDA
        if denda > 0:
            cursor.execute("""
                INSERT INTO DENDA (id_pinjam, jumlah_denda, status)
                VALUES (%s, %s, 'Belum Lunas')
            """, (id_pinjam, denda))
        
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
        SELECT p.id_pinjam, u.nama as peminjam, u.nim_nip,
               p.tgl_pinjam, p.tgl_kembali_wajib, p.tgl_kembali,
               p.status, pt_out.nama as petugas_out, pt_in.nama as petugas_in,
               b.judul, ib.barcode
        FROM PEMINJAMAN p
        JOIN USER u ON p.id_peminjam = u.id_user
        LEFT JOIN USER pt_out ON p.id_petugas_out = pt_out.id_user
        LEFT JOIN USER pt_in ON p.id_petugas_in = pt_in.id_user
        JOIN DETAIL_PINJAM dp ON p.id_pinjam = dp.id_pinjam
        JOIN ITEM_BUKU ib ON dp.id_item = ib.id_item
        JOIN BUKU b ON ib.id_buku = b.id_buku
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
        SELECT p.id_pinjam, u.nama as peminjam,
               p.tgl_pinjam, p.tgl_kembali_wajib, p.tgl_kembali,
               p.status, pt_out.nama as petugas_out
        FROM PEMINJAMAN p
        JOIN USER u ON p.id_peminjam = u.id_user
        LEFT JOIN USER pt_out ON p.id_petugas_out = pt_out.id_user
        WHERE 1=1
    """
    
    params = []
    
    if id_peminjam:
        query += " AND p.id_peminjam = %s"
        params.append(id_peminjam)
    
    if status:
        query += " AND p.status = %s"
        params.append(status)
    
    query += " ORDER BY p.tgl_pinjam DESC"
    
    cursor.execute(query, params)
    hasil = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return hasil
