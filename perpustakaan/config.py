"""
Konfigurasi Database dan Aplikasi Perpustakaan
"""

# Konfigurasi MySQL/MariaDB (phpMyAdmin)
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Default XAMPP/WAMP kosong
    'database': 'perpustakaan_db',
    'charset': 'utf8mb4'
}

# Konfigurasi Flask
class Config:
    SECRET_KEY = 'perpustakaan-secret-key-2024'
    MYSQL_HOST = DB_CONFIG['host']
    MYSQL_USER = DB_CONFIG['user']
    MYSQL_PASSWORD = DB_CONFIG['password']
    MYSQL_DB = DB_CONFIG['database']
    MYSQL_CHARSET = DB_CONFIG['charset']
