"""
Manajemen Kategori Buku
"""
import mysql.connector
from config import DB_CONFIG

def get_db_connection():
    """Membuat koneksi ke database MySQL"""
    return mysql.connector.connect(**DB_CONFIG)

def get_all_kategori():
    """Mengambil semua kategori"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT k.id_kategori, k.nama_kategori, COUNT(kb.isbn) as jumlah_buku
        FROM KATEGORI_BUKU k
        LEFT JOIN KATALOG_BUKU kb ON k.id_kategori = kb.id_kategori
        GROUP BY k.id_kategori, k.nama_kategori
        ORDER BY k.nama_kategori ASC
    """)
    
    kategori_list = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return {'kategori': kategori_list}

def get_kategori_by_id(id_kategori):
    """Mengambil detail kategori berdasarkan ID"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT k.id_kategori, k.nama_kategori, COUNT(kb.isbn) as jumlah_buku
        FROM KATEGORI_BUKU k
        LEFT JOIN KATALOG_BUKU kb ON k.id_kategori = kb.id_kategori
        WHERE k.id_kategori = %s
        GROUP BY k.id_kategori, k.nama_kategori
    """, (id_kategori,))
    
    kategori = cursor.fetchone()
    cursor.close()
    conn.close()
    
    return {'kategori': kategori} if kategori else None

def create_kategori(data):
    """Membuat kategori baru"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        INSERT INTO KATEGORI_BUKU (id_kategori, nama_kategori)
        VALUES (%s, %s)
    """
    
    try:
        cursor.execute(query, (data.get('id_kategori'), data.get('nama_kategori')))
        conn.commit()
        return {'success': True, 'message': 'Kategori berhasil dibuat'}
    except mysql.connector.Error as err:
        return {'success': False, 'error': str(err)}
    finally:
        cursor.close()
        conn.close()

def update_kategori(id_kategori, data):
    """Update data kategori"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        UPDATE KATEGORI_BUKU 
        SET nama_kategori = %s
        WHERE id_kategori = %s
    """
    
    try:
        cursor.execute(query, (data.get('nama_kategori'), id_kategori))
        conn.commit()
        return {'success': True, 'message': 'Kategori berhasil diupdate'}
    except mysql.connector.Error as err:
        return {'success': False, 'error': str(err)}
    finally:
        cursor.close()
        conn.close()

def delete_kategori(id_kategori):
    """Hapus kategori"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM KATEGORI_BUKU WHERE id_kategori = %s", (id_kategori,))
        conn.commit()
        return {'success': True, 'message': 'Kategori berhasil dihapus'}
    except mysql.connector.Error as err:
        return {'success': False, 'error': str(err)}
    finally:
        cursor.close()
        conn.close()
