"""
Manajemen Users - CRUD untuk user sistem perpustakaan
"""
import mysql.connector
from config import DB_CONFIG

def get_db_connection():
    """Membuat koneksi ke database MySQL"""
    return mysql.connector.connect(**DB_CONFIG)

def get_all_users():
    """Mengambil semua user dari database"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT id_user, username, nama, email, role, 
               DATE_FORMAT(tgl_daftar, '%d-%m-%Y') as tgl_daftar,
               status
        FROM USER
        ORDER BY tgl_daftar DESC
    """)
    
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return users

def get_user_by_id(id_user):
    """Mengambil detail user berdasarkan ID"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT id_user, username, nama, email, role, 
               DATE_FORMAT(tgl_daftar, '%d-%m-%Y') as tgl_daftar,
               status
        FROM USER
        WHERE id_user = %s
    """, (id_user,))
    
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    
    return user

def create_user(username, nama, email, password, role='MHS'):
    """Membuat user baru"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        INSERT INTO USER (username, nama, email, password, role)
        VALUES (%s, %s, %s, SHA2(%s, 256), %s)
    """
    
    try:
        cursor.execute(query, (username, nama, email, password, role))
        conn.commit()
        return {'success': True, 'message': 'User berhasil dibuat'}
    except mysql.connector.Error as err:
        return {'success': False, 'message': f'Error: {str(err)}'}
    finally:
        cursor.close()
        conn.close()

def update_user(id_user, nama, email, role, status):
    """Update data user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        UPDATE USER 
        SET nama = %s, email = %s, role = %s, status = %s
        WHERE id_user = %s
    """
    
    try:
        cursor.execute(query, (nama, email, role, status, id_user))
        conn.commit()
        return {'success': True, 'message': 'User berhasil diupdate'}
    except mysql.connector.Error as err:
        return {'success': False, 'message': f'Error: {str(err)}'}
    finally:
        cursor.close()
        conn.close()

def delete_user(id_user):
    """Hapus user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM USER WHERE id_user = %s", (id_user,))
        conn.commit()
        return {'success': True, 'message': 'User berhasil dihapus'}
    except mysql.connector.Error as err:
        return {'success': False, 'message': f'Error: {str(err)}'}
    finally:
        cursor.close()
        conn.close()

def reset_password(id_user, new_password):
    """Reset password user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        UPDATE USER 
        SET password = SHA2(%s, 256)
        WHERE id_user = %s
    """
    
    try:
        cursor.execute(query, (new_password, id_user))
        conn.commit()
        return {'success': True, 'message': 'Password berhasil direset'}
    except mysql.connector.Error as err:
        return {'success': False, 'message': f'Error: {str(err)}'}
    finally:
        cursor.close()
        conn.close()
