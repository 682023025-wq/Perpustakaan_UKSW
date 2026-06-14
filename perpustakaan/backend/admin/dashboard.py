"""
Dashboard Admin - Statistik dan overview sistem
"""
import mysql.connector
from config import DB_CONFIG

def get_db_connection():
    """Membuat koneksi ke database MySQL"""
    return mysql.connector.connect(**DB_CONFIG)

def get_dashboard_stats():
    """Mengambil statistik untuk dashboard admin"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    stats = {}
    
    # Total user
    cursor.execute("SELECT COUNT(*) as total FROM USER WHERE role IN ('MHS', 'DSN')")
    stats['total_users'] = cursor.fetchone()['total']
    
    # Total buku
    cursor.execute("SELECT COUNT(*) as total FROM BUKU")
    stats['total_buku'] = cursor.fetchone()['total']
    
    # Total peminjaman aktif
    cursor.execute("""
        SELECT COUNT(*) as total 
        FROM PEMINJAMAN 
        WHERE status = 'Dipinjam'
    """)
    stats['peminjaman_aktif'] = cursor.fetchone()['total']
    
    # Total denda belum lunas
    cursor.execute("""
        SELECT COUNT(*) as total 
        FROM DENDA 
        WHERE status = 'Belum Lunas'
    """)
    stats['denda_belum_lunas'] = cursor.fetchone()['total']
    
    # Peminjaman terbaru
    cursor.execute("""
        SELECT p.id_pinjam, u.nama as peminjam, b.judul, 
               p.tgl_pinjam, p.tgl_kembali_wajib, p.status
        FROM PEMINJAMAN p
        JOIN USER u ON p.id_peminjam = u.id_user
        JOIN DETAIL_PINJAM dp ON p.id_pinjam = dp.id_pinjam
        JOIN ITEM_BUKU ib ON dp.id_item = ib.id_item
        JOIN BUKU b ON ib.id_buku = b.id_buku
        ORDER BY p.tgl_pinjam DESC
        LIMIT 5
    """)
    stats['peminjaman_terbaru'] = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return stats

def get_recent_activities():
    """Mengambil aktivitas terbaru di sistem"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT 'peminjaman' as jenis, id_pinjam as id, 
               tgl_pinjam as tanggal, status
        FROM PEMINJAMAN
        UNION ALL
        SELECT 'pengembalian' as jenis, id_pinjam as id,
               tgl_kembali as tanggal, status
        FROM PEMINJAMAN
        WHERE tgl_kembali IS NOT NULL
        ORDER BY tanggal DESC
        LIMIT 10
    """)
    
    activities = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return activities
