"""
Admin module untuk Sistem Informasi Perpustakaan
Berisi routes untuk dashboard, users, katalog, kategori, dan rak
"""

from backend.admin.dashboard import admin_dashboard_bp
from backend.admin.users import users_bp
from backend.admin.katalog import katalog_bp
from backend.admin.kategori import kategori_bp
from backend.admin.rak import rak_bp

__all__ = [
    'admin_dashboard_bp',
    'users_bp',
    'katalog_bp',
    'kategori_bp',
    'rak_bp'
]