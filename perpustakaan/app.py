from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from functools import wraps
import sys
import os

# Tambahkan path ke sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import DB_CONFIG, APP_CONFIG, get_db_connection
from backend.auth import login_required, check_role

app = Flask(__name__)
app.secret_key = APP_CONFIG['SECRET_KEY']
app.config['UPLOAD_FOLDER'] = APP_CONFIG['UPLOAD_FOLDER']
app.config['MAX_CONTENT_LENGTH'] = APP_CONFIG['MAX_CONTENT_LENGTH']

# Import blueprints
from backend.admin.dashboard import admin_dashboard_bp
from backend.admin.users import users_bp
from backend.admin.katalog import katalog_bp
from backend.admin.kategori import kategori_bp
from backend.admin.rak import rak_bp
from backend.karyawan.dashboard import karyawan_dashboard_bp
from backend.karyawan.peminjaman import peminjaman_bp
from backend.karyawan.denda import denda_bp
from backend.karyawan.laporan import laporan_bp

app.register_blueprint(admin_dashboard_bp, url_prefix='/admin')
app.register_blueprint(users_bp, url_prefix='/admin/users')
app.register_blueprint(katalog_bp, url_prefix='/admin/katalog')
app.register_blueprint(kategori_bp, url_prefix='/admin/kategori')
app.register_blueprint(rak_bp, url_prefix='/admin/rak')
app.register_blueprint(karyawan_dashboard_bp, url_prefix='/karyawan')
app.register_blueprint(peminjaman_bp, url_prefix='/karyawan/peminjaman')
app.register_blueprint(denda_bp, url_prefix='/karyawan/denda')
app.register_blueprint(laporan_bp, url_prefix='/karyawan/laporan')

@app.route('/')
def index():
    if 'user_id' in session:
        if session['role'] == 'SPRADM':
            return redirect(url_for('admin_dashboard'))
        elif session['role'] == 'PTGS':
            return redirect(url_for('karyawan_dashboard'))
        else:
            return redirect(url_for('user_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT u.id_user, u.username, u.nama_lengkap, u.id_role, r.nama_role 
                FROM USERS u
                JOIN ROLES r ON u.id_role = r.id_role
                WHERE u.username = %s AND u.password = %s AND u.status_aktif = 'Aktif'
            """
            cursor.execute(query, (username, password))
            user = cursor.fetchone()
            cursor.close()
            connection.close()
            
            if user:
                session['user_id'] = user['id_user']
                session['username'] = user['username']
                session['nama_lengkap'] = user['nama_lengkap']
                session['role'] = user['id_role']
                session['role_name'] = user['nama_role']
                
                if user['id_role'] == 'SPRADM':
                    return redirect(url_for('admin_dashboard'))
                elif user['id_role'] == 'PTGS':
                    return redirect(url_for('karyawan_dashboard'))
                else:
                    flash('Login berhasil sebagai User. Namun akses terbatas.', 'info')
                    return redirect(url_for('index'))
            else:
                flash('Username atau password salah, atau akun tidak aktif.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Halaman Admin Dashboard
@app.route('/admin/dashboard')
@login_required
@check_role(['SPRADM'])
def admin_dashboard():
    return render_template('admin/dashboard.html')

# Halaman Karyawan Dashboard
@app.route('/karyawan/dashboard')
@login_required
@check_role(['PTGS'])
def karyawan_dashboard():
    return render_template('karyawan/dashboard.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
