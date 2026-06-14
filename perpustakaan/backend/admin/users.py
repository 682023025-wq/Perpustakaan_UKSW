"""
Manajemen Users - CRUD untuk user sistem perpustakaan
"""
import mysql.connector
from config import DB_CONFIG

def get_db_connection():
    """Membuat koneksi ke database MySQL"""
    return mysql.connector.connect(**DB_CONFIG)

def get_all_users(role=None, status=None):
    """Mengambil semua user dari database dengan filter opsional"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT u.id_user, u.username, u.nama_lengkap, u.email, u.no_telepon,
               u.program_studi, u.fakultas, u.status_aktif, u.id_role,
               r.nama_role, DATE_FORMAT(u.created_at, '%Y-%m-%d %H:%i:%s') as created_at
        FROM USERS u
        LEFT JOIN ROLES r ON u.id_role = r.id_role
        WHERE 1=1
    """
    params = []
    
    if role:
        query += " AND u.id_role = %s"
        params.append(role)
    
    if status:
        query += " AND u.status_aktif = %s"
        params.append(status)
    
    query += " ORDER BY u.created_at DESC"
    
    cursor.execute(query, params)
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return {'users': users}

def get_user_by_id(id_user):
    """Mengambil detail user berdasarkan ID"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT u.id_user, u.username, u.password, u.nama_lengkap, u.email, u.no_telepon,
               u.program_studi, u.fakultas, u.status_aktif, u.alasan_nonaktif, 
               u.tgl_nonaktif, u.dinonaktifkan_oleh, u.id_role,
               r.nama_role, DATE_FORMAT(u.created_at, '%Y-%m-%d %H:%i:%s') as created_at
        FROM USERS u
        LEFT JOIN ROLES r ON u.id_role = r.id_role
        WHERE u.id_user = %s
    """, (id_user,))
    
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    
    return {'user': user} if user else None

def create_user(data):
    """Membuat user baru"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        INSERT INTO USERS (id_user, username, password, nama_lengkap, email, no_telepon,
                          program_studi, fakultas, id_role, status_aktif)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    try:
        cursor.execute(query, (
            data.get('id_user'),
            data.get('username'),
            data.get('password', 'password123'),
            data.get('nama_lengkap'),
            data.get('email'),
            data.get('no_telepon'),
            data.get('program_studi'),
            data.get('fakultas'),
            data.get('id_role'),
            data.get('status_aktif', 'Aktif')
        ))
        conn.commit()
        return {'success': True, 'message': 'User berhasil dibuat'}
    except mysql.connector.Error as err:
        return {'success': False, 'error': str(err)}
    finally:
        cursor.close()
        conn.close()

def update_user(id_user, data):
    """Update data user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        UPDATE USERS 
        SET username = %s, nama_lengkap = %s, email = %s, no_telepon = %s,
            program_studi = %s, fakultas = %s, id_role = %s, status_aktif = %s
        WHERE id_user = %s
    """
    
    try:
        cursor.execute(query, (
            data.get('username'),
            data.get('nama_lengkap'),
            data.get('email'),
            data.get('no_telepon'),
            data.get('program_studi'),
            data.get('fakultas'),
            data.get('id_role'),
            data.get('status_aktif'),
            id_user
        ))
        
        # Update password jika ada
        if data.get('password'):
            cursor.execute("UPDATE USERS SET password = %s WHERE id_user = %s", 
                          (data.get('password'), id_user))
        
        conn.commit()
        return {'success': True, 'message': 'User berhasil diupdate'}
    except mysql.connector.Error as err:
        return {'success': False, 'error': str(err)}
    finally:
        cursor.close()
        conn.close()

def delete_user(id_user):
    """Hapus user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM USERS WHERE id_user = %s", (id_user,))
        conn.commit()
        return {'success': True, 'message': 'User berhasil dihapus'}
    except mysql.connector.Error as err:
        return {'success': False, 'error': str(err)}
    finally:
        cursor.close()
        conn.close()
