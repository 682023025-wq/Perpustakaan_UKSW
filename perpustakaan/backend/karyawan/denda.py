"""
Manajemen Denda Perpustakaan
"""
import mysql.connector
from config import DB_CONFIG

def get_db_connection():
    """Membuat koneksi ke database MySQL"""
    return mysql.connector.connect(**DB_CONFIG)

def get_all_denda(status=None):
    """Mengambil semua denda dengan filter status opsional"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT d.id_denda, d.id_pinjam, u.nama_lengkap as peminjam,
               d.nominal_denda, d.status_bayar, d.tgl_bayar,
               p.tgl_jatuh_tempo, p.tgl_kembali
        FROM DENDA d
        JOIN PEMINJAMAN p ON d.id_pinjam = p.id_pinjam
        JOIN USERS u ON p.id_peminjam = u.id_user
        WHERE 1=1
    """
    
    params = []
    
    if status:
        query += " AND d.status_bayar = %s"
        params.append(status)
    
    query += " ORDER BY d.id_denda DESC"
    
    cursor.execute(query, params)
    denda_list = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return denda_list

def get_denda_by_id(id_denda):
    """Mengambil detail denda berdasarkan ID"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT d.*, u.nama_lengkap as peminjam,
               p.tgl_jatuh_tempo, p.tgl_kembali
        FROM DENDA d
        JOIN PEMINJAMAN p ON d.id_pinjam = p.id_pinjam
        JOIN USERS u ON p.id_peminjam = u.id_user
        WHERE d.id_denda = %s
    """, (id_denda,))
    
    denda = cursor.fetchone()
    cursor.close()
    conn.close()
    
    return denda

def bayar_denda(id_denda, id_petugas):
    """
    Membayar denda
    Parameter:
        - id_denda: ID denda yang akan dibayar
        - id_petugas: ID petugas yang menerima pembayaran
    Returns: dict dengan status pembayaran
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Cek apakah denda ada dan belum lunas
        cursor.execute("""
            SELECT nominal_denda FROM DENDA 
            WHERE id_denda = %s AND status_bayar = 'Belum Lunas'
        """, (id_denda,))
        
        denda = cursor.fetchone()
        
        if not denda:
            return {'success': False, 'message': 'Denda tidak ditemukan atau sudah lunas'}
        
        # Update status denda menjadi Lunas
        from datetime import date
        cursor.execute("""
            UPDATE DENDA 
            SET status_bayar = 'Lunas', tgl_bayar = %s
            WHERE id_denda = %s
        """, (date.today(), id_denda))
        
        conn.commit()
        
        return {
            'success': True,
            'message': f'Pembayaran denda berhasil. Jumlah: Rp {denda["nominal_denda"]:,}'
        }
        
    except mysql.connector.Error as err:
        conn.rollback()
        return {'success': False, 'message': f'Error: {str(err)}'}
    finally:
        cursor.close()
        conn.close()

def get_total_denda_belum_lunas(id_peminjam=None):
    """Menghitung total denda yang belum lunas"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT SUM(nominal_denda) as total 
        FROM DENDA 
        WHERE status_bayar = 'Belum Lunas'
    """
    
    params = []
    
    if id_peminjam:
        query += """
            AND id_pinjam IN (
                SELECT id_pinjam FROM PEMINJAMAN WHERE id_peminjam = %s
            )
        """
        params.append(id_peminjam)
    
    cursor.execute(query, params)
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    
    return result['total'] or 0

def get_statistik_denda():
    """Mengambil statistik denda"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    stats = {}
    
    # Total denda belum lunas
    cursor.execute("""
        SELECT COUNT(*) as jumlah, SUM(nominal_denda) as total 
        FROM DENDA 
        WHERE status_bayar = 'Belum Lunas'
    """)
    result = cursor.fetchone()
    stats['belum_lunas'] = {
        'jumlah': result['jumlah'] or 0,
        'total': float(result['total']) if result['total'] else 0
    }
    
    # Total denda lunas bulan ini
    cursor.execute("""
        SELECT COUNT(*) as jumlah, SUM(nominal_denda) as total 
        FROM DENDA 
        WHERE status_bayar = 'Lunas' 
          AND MONTH(tgl_bayar) = MONTH(CURDATE())
          AND YEAR(tgl_bayar) = YEAR(CURDATE())
    """)
    result = cursor.fetchone()
    stats['lunas_bulan_ini'] = {
        'jumlah': result['jumlah'] or 0,
        'total': float(result['total']) if result['total'] else 0
    }
    
    cursor.close()
    conn.close()
    
    return stats
