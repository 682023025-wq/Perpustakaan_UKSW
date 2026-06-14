"""
Dashboard Karyawan - Statistik dan operasional perpustakaan
"""
import mysql.connector
from config import DB_CONFIG

def get_db_connection():
    """Membuat koneksi ke database MySQL"""
    return mysql.connector.connect(**DB_CONFIG)

def get_dashboard_stats(id_petugas=None):
    """Mengambil statistik untuk dashboard karyawan"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    stats = {}
    
    # Total peminjaman aktif
    cursor.execute("""
        SELECT COUNT(*) as total 
        FROM PEMINJAMAN 
        WHERE status = 'Dipinjam'
    """)
    stats['peminjaman_aktif'] = cursor.fetchone()['total']
    
    # Peminjaman yang harus kembali hari ini
    cursor.execute("""
        SELECT COUNT(*) as total 
        FROM PEMINJAMAN 
        WHERE tgl_kembali_wajib = CURDATE() AND status = 'Dipinjam'
    """)
    stats['kembali_hari_ini'] = cursor.fetchone()['total']
    
    # Total denda belum lunas
    cursor.execute("""
        SELECT COUNT(*) as total 
        FROM DENDA 
        WHERE status = 'Belum Lunas'
    """)
    stats['denda_belum_lunas'] = cursor.fetchone()['total']
    
    # Buku tersedia
    cursor.execute("""
        SELECT COUNT(*) as total 
        FROM ITEM_BUKU 
        WHERE status = 'Tersedia'
    """)
    stats['buku_tersedia'] = cursor.fetchone()['total']
    
    # Peminjaman yang ditangani petugas ini (jika id_petugas diberikan)
    if id_petugas:
        cursor.execute("""
            SELECT COUNT(*) as total 
            FROM PEMINJAMAN 
            WHERE id_petugas_out = %s AND status = 'Dipinjam'
        """, (id_petugas,))
        stats['peminjaman_saya'] = cursor.fetchone()['total']
    
    # Transaksi terbaru
    cursor.execute("""
        SELECT p.id_pinjam, u.nama as peminjam, 
               p.tgl_pinjam, p.tgl_kembali_wajib, p.status,
               pt.nama as petugas_out
        FROM PEMINJAMAN p
        JOIN USER u ON p.id_peminjam = u.id_user
        LEFT JOIN USER pt ON p.id_petugas_out = pt.id_user
        ORDER BY p.tgl_pinjam DESC
        LIMIT 5
    """)
    stats['transaksi_terbaru'] = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return stats

def get_peminjaman_perlu_dikembalikan():
    """Mengambil daftar peminjaman yang perlu dikembalikan segera"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT p.id_pinjam, u.nama as peminjam, b.judul,
               p.tgl_pinjam, p.tgl_kembali_wajib,
               DATEDIFF(CURDATE(), p.tgl_kembali_wajib) as hari_terlambat
        FROM PEMINJAMAN p
        JOIN USER u ON p.id_peminjam = u.id_user
        JOIN DETAIL_PINJAM dp ON p.id_pinjam = dp.id_pinjam
        JOIN ITEM_BUKU ib ON dp.id_item = ib.id_item
        JOIN BUKU b ON ib.id_buku = b.id_buku
        WHERE p.status = 'Dipinjam' 
          AND p.tgl_kembali_wajib <= CURDATE()
        ORDER BY p.tgl_kembali_wajib ASC
        LIMIT 10
    """)
    
    hasil = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return hasil
