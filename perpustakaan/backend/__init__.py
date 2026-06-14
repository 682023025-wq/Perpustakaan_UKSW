"""
Backend package untuk Sistem Informasi Perpustakaan
Berisi modul-modul untuk Admin dan Karyawan
"""

from backend.admin.dashboard import admin_dashboard_bp
from backend.admin.users import users_bp
from backend.admin.katalog import katalog_bp
from backend.admin.kategori import kategori_bp
from backend.admin.rak import rak_bp
from backend.karyawan.dashboard import karyawan_dashboard_bp
from backend.karyawan.peminjaman import peminjaman_bp
from backend.karyawan.denda import denda_bp
from backend.karyawan.laporan import laporan_bp

__all__ = [
    'admin_dashboard_bp',
    'users_bp',
    'katalog_bp',
    'kategori_bp',
    'rak_bp',
    'karyawan_dashboard_bp',
    'peminjaman_bp',
    'denda_bp',
    'laporan_bp'
]
