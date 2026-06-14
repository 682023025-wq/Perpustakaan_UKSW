"""
Karyawan module untuk Sistem Informasi Perpustakaan
Berisi routes untuk dashboard, peminjaman, pengembalian, denda, dan laporan
"""

from backend.karyawan.dashboard import karyawan_dashboard_bp
from backend.karyawan.peminjaman import peminjaman_bp
from backend.karyawan.pengembalian import pengembalian_bp
from backend.karyawan.denda import denda_bp
from backend.karyawan.laporan import laporan_bp

__all__ = [
    'karyawan_dashboard_bp',
    'peminjaman_bp',
    'pengembalian_bp',
    'denda_bp',
    'laporan_bp'
]
