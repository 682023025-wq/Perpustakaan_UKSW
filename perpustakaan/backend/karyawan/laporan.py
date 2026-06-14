"""
Laporan dan Statistik Perpustakaan
"""
import mysql.connector
from config import DB_CONFIG
from datetime import datetime, timedelta

def get_db_connection():
    """Membuat koneksi ke database MySQL"""
    return mysql.connector.connect(**DB_CONFIG)

def get_laporan_peminjaman(tgl_mulai=None, tgl_akhir=None):
    """
    Laporan peminjaman dengan filter tanggal
    Default: 30 hari terakhir
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if not tgl_mulai:
        tgl_mulai = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    if not tgl_akhir:
        tgl_akhir = datetime.now().strftime('%Y-%m-%d')
    
    query = """
        SELECT p.id_pinjam, u.nama as peminjam, u.nim_nip,
               p.tgl_pinjam, p.tgl_kembali_wajib, p.tgl_kembali,
               p.status, pt_out.nama as petugas_out, pt_in.nama as petugas_in,
               GROUP_CONCAT(b.judul SEPARATOR ', ') as buku_dipinjam
        FROM PEMINJAMAN p
        JOIN USER u ON p.id_peminjam = u.id_user
        LEFT JOIN USER pt_out ON p.id_petugas_out = pt_out.id_user
        LEFT JOIN USER pt_in ON p.id_petugas_in = pt_in.id_user
        JOIN DETAIL_PINJAM dp ON p.id_pinjam = dp.id_pinjam
        JOIN ITEM_BUKU ib ON dp.id_item = ib.id_item
        JOIN BUKU b ON ib.id_buku = b.id_buku
        WHERE p.tgl_pinjam BETWEEN %s AND %s
        GROUP BY p.id_pinjam
        ORDER BY p.tgl_pinjam DESC
    """
    
    cursor.execute(query, (tgl_mulai, tgl_akhir))
    laporan = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return laporan

def get_laporan_pengembalian(tgl_mulai=None, tgl_akhir=None):
    """
    Laporan pengembalian dengan filter tanggal
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if not tgl_mulai:
        tgl_mulai = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    if not tgl_akhir:
        tgl_akhir = datetime.now().strftime('%Y-%m-%d')
    
    query = """
        SELECT p.id_pinjam, u.nama as peminjam, u.nim_nip,
               p.tgl_pinjam, p.tgl_kembali_wajib, p.tgl_kembali,
               pt_in.nama as petugas_in,
               GROUP_CONCAT(b.judul SEPARATOR ', ') as buku_dikembalikan,
               CASE WHEN DATEDIFF(p.tgl_kembali, p.tgl_kembali_wajib) > 0 
                    THEN 'Terlambat' ELSE 'Tepat Waktu' END as status_pengembalian
        FROM PEMINJAMAN p
        JOIN USER u ON p.id_peminjam = u.id_user
        LEFT JOIN USER pt_in ON p.id_petugas_in = pt_in.id_user
        JOIN DETAIL_PINJAM dp ON p.id_pinjam = dp.id_pinjam
        JOIN ITEM_BUKU ib ON dp.id_item = ib.id_item
        JOIN BUKU b ON ib.id_buku = b.id_buku
        WHERE p.tgl_kembali BETWEEN %s AND %s
          AND p.status = 'Dikembalikan'
        GROUP BY p.id_pinjam
        ORDER BY p.tgl_kembali DESC
    """
    
    cursor.execute(query, (tgl_mulai, tgl_akhir))
    laporan = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return laporan

def get_laporan_denda(tgl_mulai=None, tgl_akhir=None):
    """
    Laporan denda dengan filter tanggal
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if not tgl_mulai:
        tgl_mulai = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    if not tgl_akhir:
        tgl_akhir = datetime.now().strftime('%Y-%m-%d')
    
    query = """
        SELECT d.id_denda, d.id_pinjam, u.nama as peminjam, u.nim_nip,
               d.jumlah_denda, d.status, d.tgl_bayar,
               p.tgl_kembali_wajib, p.tgl_kembali
        FROM DENDA d
        JOIN PEMINJAMAN p ON d.id_pinjam = p.id_pinjam
        JOIN USER u ON p.id_peminjam = u.id_user
        WHERE (d.tgl_bayar BETWEEN %s AND %s OR d.tgl_bayar IS NULL)
        ORDER BY d.id_denda DESC
    """
    
    cursor.execute(query, (tgl_mulai, tgl_akhir))
    laporan = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return laporan

def get_statistik_bulanan(bulan=None, tahun=None):
    """
    Statistik bulanan perpustakaan
    """
    from datetime import datetime
    
    if not bulan:
        bulan = datetime.now().month
    if not tahun:
        tahun = datetime.now().year
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    stats = {}
    
    # Total peminjaman bulan ini
    cursor.execute("""
        SELECT COUNT(*) as total 
        FROM PEMINJAMAN 
        WHERE MONTH(tgl_pinjam) = %s AND YEAR(tgl_pinjam) = %s
    """, (bulan, tahun))
    stats['total_peminjaman'] = cursor.fetchone()['total']
    
    # Total pengembalian bulan ini
    cursor.execute("""
        SELECT COUNT(*) as total 
        FROM PEMINJAMAN 
        WHERE MONTH(tgl_kembali) = %s AND YEAR(tgl_kembali) = %s
          AND status = 'Dikembalikan'
    """, (bulan, tahun))
    stats['total_pengembalian'] = cursor.fetchone()['total']
    
    # Total denda lunas bulan ini
    cursor.execute("""
        SELECT SUM(jumlah_denda) as total 
        FROM DENDA 
        WHERE MONTH(tgl_bayar) = %s AND YEAR(tgl_bayar) = %s
          AND status = 'Lunas'
    """, (bulan, tahun))
    result = cursor.fetchone()
    stats['total_denda_lunas'] = result['total'] or 0
    
    # Buku paling banyak dipinjam bulan ini
    cursor.execute("""
        SELECT b.judul, COUNT(dp.id_item) as jumlah_pinjam
        FROM DETAIL_PINJAM dp
        JOIN ITEM_BUKU ib ON dp.id_item = ib.id_item
        JOIN BUKU b ON ib.id_buku = b.id_buku
        JOIN PEMINJAMAN p ON dp.id_pinjam = p.id_pinjam
        WHERE MONTH(p.tgl_pinjam) = %s AND YEAR(p.tgl_pinjam) = %s
        GROUP BY b.id_buku
        ORDER BY jumlah_pinjam DESC
        LIMIT 5
    """, (bulan, tahun))
    stats['buku_populer'] = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return stats

def get_grafik_peminjaman_per_hari(bulan=None, tahun=None):
    """Data grafik peminjaman per hari dalam sebulan"""
    from datetime import datetime
    
    if not bulan:
        bulan = datetime.now().month
    if not tahun:
        tahun = datetime.now().year
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT DAY(tgl_pinjam) as hari, COUNT(*) as jumlah
        FROM PEMINJAMAN
        WHERE MONTH(tgl_pinjam) = %s AND YEAR(tgl_pinjam) = %s
        GROUP BY DAY(tgl_pinjam)
        ORDER BY hari ASC
    """, (bulan, tahun))
    
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return data
