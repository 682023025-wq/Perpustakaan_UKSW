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
        SELECT r.*, COUNT(ib.id_item) as jumlah_buku
        FROM RAK r
        LEFT JOIN ITEM_BUKU ib ON r.id_rak = ib.id_rak
        GROUP BY r.id_rak
        ORDER BY r.lokasi ASC
    """)
    
    rak_list = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return rak_list

def get_rak_by_id(id_rak):
    """Mengambil detail rak berdasarkan ID"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT r.*, COUNT(ib.id_item) as jumlah_buku
        FROM RAK r
        LEFT JOIN ITEM_BUKU ib ON r.id_rak = ib.id_rak
        WHERE r.id_rak = %s
        GROUP BY r.id_rak
    """, (id_rak,))
    
    rak = cursor.fetchone()
    cursor.close()
    conn.close()
    
    return rak

def create_rak(kode_rak, lokasi, kapasitas=50):
    """Membuat rak baru"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        INSERT INTO RAK (kode_rak, lokasi, kapasitas)
        VALUES (%s, %s, %s)
    """
    
    try:
        cursor.execute(query, (kode_rak, lokasi, kapasitas))
        conn.commit()
        id_rak = cursor.lastrowid
        return {'success': True, 'message': 'Rak berhasil dibuat', 'id_rak': id_rak}
    except mysql.connector.Error as err:
        return {'success': False, 'message': f'Error: {str(err)}'}
    finally:
        cursor.close()
        conn.close()

def update_rak(id_rak, kode_rak, lokasi, kapasitas):
    """Update data rak"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        UPDATE RAK 
        SET kode_rak = %s, lokasi = %s, kapasitas = %s
        WHERE id_rak = %s
    """
    
    try:
        cursor.execute(query, (kode_rak, lokasi, kapasitas, id_rak))
        conn.commit()
        return {'success': True, 'message': 'Rak berhasil diupdate'}
    except mysql.connector.Error as err:
        return {'success': False, 'message': f'Error: {str(err)}'}
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
        return {'success': False, 'message': f'Error: {str(err)}'}
    finally:
        cursor.close()
        conn.close()
