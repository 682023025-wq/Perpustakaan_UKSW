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
        SELECT k.*, COUNT(b.id_buku) as jumlah_buku
        FROM KATEGORI k
        LEFT JOIN BUKU b ON k.id_kategori = b.id_kategori
        GROUP BY k.id_kategori
        ORDER BY k.nama_kategori ASC
    """)
    
    kategori_list = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return kategori_list

def get_kategori_by_id(id_kategori):
    """Mengambil detail kategori berdasarkan ID"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT k.*, COUNT(b.id_buku) as jumlah_buku
        FROM KATEGORI k
        LEFT JOIN BUKU b ON k.id_kategori = b.id_kategori
        WHERE k.id_kategori = %s
        GROUP BY k.id_kategori
    """, (id_kategori,))
    
    kategori = cursor.fetchone()
    cursor.close()
    conn.close()
    
    return kategori

def create_kategori(nama_kategori, deskripsi=None):
    """Membuat kategori baru"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        INSERT INTO KATEGORI (nama_kategori, deskripsi)
        VALUES (%s, %s)
    """
    
    try:
        cursor.execute(query, (nama_kategori, deskripsi))
        conn.commit()
        id_kategori = cursor.lastrowid
        return {'success': True, 'message': 'Kategori berhasil dibuat', 'id_kategori': id_kategori}
    except mysql.connector.Error as err:
        return {'success': False, 'message': f'Error: {str(err)}'}
    finally:
        cursor.close()
        conn.close()

def update_kategori(id_kategori, nama_kategori, deskripsi=None):
    """Update data kategori"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        UPDATE KATEGORI 
        SET nama_kategori = %s, deskripsi = %s
        WHERE id_kategori = %s
    """
    
    try:
        cursor.execute(query, (nama_kategori, deskripsi, id_kategori))
        conn.commit()
        return {'success': True, 'message': 'Kategori berhasil diupdate'}
    except mysql.connector.Error as err:
        return {'success': False, 'message': f'Error: {str(err)}'}
    finally:
        cursor.close()
        conn.close()

def delete_kategori(id_kategori):
    """Hapus kategori"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM KATEGORI WHERE id_kategori = %s", (id_kategori,))
        conn.commit()
        return {'success': True, 'message': 'Kategori berhasil dihapus'}
    except mysql.connector.Error as err:
        return {'success': False, 'message': f'Error: {str(err)}'}
    finally:
        cursor.close()
        conn.close()
