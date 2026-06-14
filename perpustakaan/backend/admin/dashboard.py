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
    
    # Total user (MHS + DSN)
    cursor.execute("SELECT COUNT(*) as total FROM USERS WHERE id_role IN ('MHS', 'DSN')")
    stats['total_users'] = cursor.fetchone()['total']
    
    # Total buku (katalog)
    cursor.execute("SELECT COUNT(*) as total FROM KATALOG_BUKU")
    stats['total_buku'] = cursor.fetchone()['total']
    
    # Total item buku
    cursor.execute("SELECT COUNT(*) as total FROM ITEM_BUKU")
    stats['total_item'] = cursor.fetchone()['total']
    
    # Total peminjaman aktif
    cursor.execute("""
        SELECT COUNT(*) as total 
        FROM PEMINJAMAN 
        WHERE status_transaksi = 'Dipinjam'
    """)
    stats['peminjaman_aktif'] = cursor.fetchone()['total']
    
    # Total denda belum lunas
    cursor.execute("""
        SELECT COUNT(*) as total 
        FROM DENDA 
        WHERE status_bayar = 'Belum Lunas'
    """)
    stats['denda_belum_lunas'] = cursor.fetchone()['total']
    
    # Peminjaman terbaru
    cursor.execute("""
        SELECT p.id_pinjam, u.nama_lengkap as peminjam, k.judul, 
               p.tgl_pinjam, p.tgl_jatuh_tempo, p.status_transaksi
        FROM PEMINJAMAN p
        JOIN USERS u ON p.id_peminjam = u.id_user
        JOIN ITEM_BUKU ib ON p.id_barcode = ib.id_barcode
        JOIN KATALOG_BUKU k ON ib.isbn = k.isbn
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
               tgl_pinjam as tanggal, status_transaksi as status
        FROM PEMINJAMAN
        UNION ALL
        SELECT 'pengembalian' as jenis, id_pinjam as id,
               tgl_kembali as tanggal, status_transaksi as status
        FROM PEMINJAMAN
        WHERE tgl_kembali IS NOT NULL
        ORDER BY tanggal DESC
        LIMIT 10
    """)
    
    activities = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return activities
