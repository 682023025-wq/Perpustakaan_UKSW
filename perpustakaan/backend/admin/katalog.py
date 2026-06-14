"""
Manajemen Katalog Buku - CRUD untuk buku dan item buku
"""
import mysql.connector
from config import DB_CONFIG

def get_db_connection():
    """Membuat koneksi ke database MySQL"""
    return mysql.connector.connect(**DB_CONFIG)

def get_all_buku():
    """Mengambil semua buku dengan informasi lengkap"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT b.id_buku, b.judul, b.penulis, b.penerbit, b.tahun_terbit,
               b.isbn, k.nama_kategori, COUNT(ib.id_item) as total_eksemplar,
               SUM(CASE WHEN ib.status = 'Tersedia' THEN 1 ELSE 0 END) as tersedia
        FROM BUKU b
        LEFT JOIN KATEGORI k ON b.id_kategori = k.id_kategori
        LEFT JOIN ITEM_BUKU ib ON b.id_buku = ib.id_buku
        GROUP BY b.id_buku
        ORDER BY b.judul ASC
    """)
    
    buku_list = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return buku_list

def get_buku_by_id(id_buku):
    """Mengambil detail buku berdasarkan ID"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT b.*, k.nama_kategori
        FROM BUKU b
        LEFT JOIN KATEGORI k ON b.id_kategori = k.id_kategori
        WHERE b.id_buku = %s
    """, (id_buku,))
    
    buku = cursor.fetchone()
    cursor.close()
    conn.close()
    
    return buku

def create_buku(judul, penulis, penerbit, tahun_terbit, isbn, id_kategori, deskripsi=None):
    """Membuat buku baru"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        INSERT INTO BUKU (judul, penulis, penerbit, tahun_terbit, isbn, id_kategori, deskripsi)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    
    try:
        cursor.execute(query, (judul, penulis, penerbit, tahun_terbit, isbn, id_kategori, deskripsi))
        conn.commit()
        id_buku = cursor.lastrowid
        return {'success': True, 'message': 'Buku berhasil dibuat', 'id_buku': id_buku}
    except mysql.connector.Error as err:
        return {'success': False, 'message': f'Error: {str(err)}'}
    finally:
        cursor.close()
        conn.close()

def update_buku(id_buku, judul, penulis, penerbit, tahun_terbit, isbn, id_kategori, deskripsi=None):
    """Update data buku"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        UPDATE BUKU 
        SET judul = %s, penulis = %s, penerbit = %s, 
            tahun_terbit = %s, isbn = %s, id_kategori = %s, deskripsi = %s
        WHERE id_buku = %s
    """
    
    try:
        cursor.execute(query, (judul, penulis, penerbit, tahun_terbit, isbn, id_kategori, deskripsi, id_buku))
        conn.commit()
        return {'success': True, 'message': 'Buku berhasil diupdate'}
    except mysql.connector.Error as err:
        return {'success': False, 'message': f'Error: {str(err)}'}
    finally:
        cursor.close()
        conn.close()

def delete_buku(id_buku):
    """Hapus buku"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Hapus item buku terlebih dahulu
        cursor.execute("DELETE FROM ITEM_BUKU WHERE id_buku = %s", (id_buku,))
        # Hapus buku
        cursor.execute("DELETE FROM BUKU WHERE id_buku = %s", (id_buku,))
        conn.commit()
        return {'success': True, 'message': 'Buku berhasil dihapus'}
    except mysql.connector.Error as err:
        return {'success': False, 'message': f'Error: {str(err)}'}
    finally:
        cursor.close()
        conn.close()

def add_item_buku(id_buku, barcode, id_rak):
    """Menambahkan eksemplar buku baru"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        INSERT INTO ITEM_BUKU (id_buku, barcode, id_rak, status)
        VALUES (%s, %s, %s, 'Tersedia')
    """
    
    try:
        cursor.execute(query, (id_buku, barcode, id_rak))
        conn.commit()
        return {'success': True, 'message': 'Item buku berhasil ditambahkan'}
    except mysql.connector.Error as err:
        return {'success': False, 'message': f'Error: {str(err)}'}
    finally:
        cursor.close()
        conn.close()

def search_buku(keyword):
    """Mencari buku berdasarkan judul, penulis, atau ISBN"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT b.id_buku, b.judul, b.penulis, b.penerbit, b.tahun_terbit,
               b.isbn, k.nama_kategori
        FROM BUKU b
        LEFT JOIN KATEGORI k ON b.id_kategori = k.id_kategori
        WHERE b.judul LIKE %s OR b.penulis LIKE %s OR b.isbn LIKE %s
        ORDER BY b.judul ASC
    """
    
    search_term = f"%{keyword}%"
    cursor.execute(query, (search_term, search_term, search_term))
    
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return results
