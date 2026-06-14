"""
Manajemen Rak Buku
"""
import mysql.connector
from config import DB_CONFIG

def get_db_connection():
    """Membuat koneksi ke database MySQL"""
    return mysql.connector.connect(**DB_CONFIG)

def get_all_rak():
    """Mengambil semua rak"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT r.id_rak, r.nama_rak, r.lokasi_detail, COUNT(ib.id_barcode) as jumlah_buku
        FROM RAK r
        LEFT JOIN ITEM_BUKU ib ON r.id_rak = ib.id_rak
        GROUP BY r.id_rak, r.nama_rak, r.lokasi_detail
        ORDER BY r.nama_rak ASC
    """)
    
    rak_list = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return {'rak': rak_list}

def get_rak_by_id(id_rak):
    """Mengambil detail rak berdasarkan ID"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT r.id_rak, r.nama_rak, r.lokasi_detail, COUNT(ib.id_barcode) as jumlah_buku
        FROM RAK r
        LEFT JOIN ITEM_BUKU ib ON r.id_rak = ib.id_rak
        WHERE r.id_rak = %s
        GROUP BY r.id_rak, r.nama_rak, r.lokasi_detail
    """, (id_rak,))
    
    rak = cursor.fetchone()
    cursor.close()
    conn.close()
    
    return {'rak': rak} if rak else None

def create_rak(data):
    """Membuat rak baru"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        INSERT INTO RAK (id_rak, nama_rak, lokasi_detail)
        VALUES (%s, %s, %s)
    """
    
    try:
        cursor.execute(query, (data.get('id_rak'), data.get('nama_rak'), data.get('lokasi_detail')))
        conn.commit()
        return {'success': True, 'message': 'Rak berhasil dibuat'}
    except mysql.connector.Error as err:
        return {'success': False, 'error': str(err)}
    finally:
        cursor.close()
        conn.close()

def update_rak(id_rak, data):
    """Update data rak"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        UPDATE RAK 
        SET nama_rak = %s, lokasi_detail = %s
        WHERE id_rak = %s
    """
    
    try:
        cursor.execute(query, (data.get('nama_rak'), data.get('lokasi_detail'), id_rak))
        conn.commit()
        return {'success': True, 'message': 'Rak berhasil diupdate'}
    except mysql.connector.Error as err:
        return {'success': False, 'error': str(err)}
    finally:
        cursor.close()
        conn.close()

def delete_rak(id_rak):
    """Hapus rak"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM RAK WHERE id_rak = %s", (id_rak,))
        conn.commit()
        return {'success': True, 'message': 'Rak berhasil dihapus'}
    except mysql.connector.Error as err:
        return {'success': False, 'error': str(err)}
    finally:
        cursor.close()
        conn.close()
