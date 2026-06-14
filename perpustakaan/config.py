import mysql.connector
from mysql.connector import Error

# Konfigurasi Database
DB_CONFIG = {
    'host': 'localhost',
    'database': 'db_perpustakaan',
    'user': 'root',
    'password': ''  # Sesuaikan dengan password MySQL Anda
}

def get_db_connection():
    """Membuat koneksi ke database"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None

# Konfigurasi Aplikasi
APP_CONFIG = {
    'SECRET_KEY': 'your-secret-key-here',
    'UPLOAD_FOLDER': 'static/uploads',
    'MAX_CONTENT_LENGTH': 16 * 1024 * 1024  # 16MB max upload
}
