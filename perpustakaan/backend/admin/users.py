from flask import Blueprint, render_template, request, jsonify, session
from config import get_db_connection
from backend.auth import login_required, check_role
from werkzeug.security import generate_password_hash 

users_bp = Blueprint('users', __name__)

@users_bp.route('/')
@login_required
@check_role(['SPRADM'])
def index():
    return render_template('admin/users.html')

@users_bp.route('/api/users', methods=['GET'])
@login_required
@check_role(['SPRADM'])
def get_users():
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT u.*, r.nama_role 
            FROM USERS u
            JOIN ROLES r ON u.id_role = r.id_role
            ORDER BY u.created_at DESC
        """
        cursor.execute(query)
        users = cursor.fetchall()
        cursor.close()
        connection.close()
        return jsonify(users)
    return jsonify([]), 500

@users_bp.route('/api/users', methods=['POST'])
@login_required
@check_role(['SPRADM'])
def create_user():
    data = request.json
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        try:
            # PERBAIKAN: Cek duplikasi username atau email
            cursor.execute("SELECT id_user FROM USERS WHERE username = %s OR email = %s", 
                           (data['username'], data['email']))
            if cursor.fetchone():
                return jsonify({'success': False, 'error': 'Username atau Email sudah terdaftar!'}), 400

            # PERBAIKAN: Hash password sebelum disimpan
            hashed_password = generate_password_hash(data['password'])
            
            # PERBAIKAN: Tambahkan status_aktif ke dalam query
            query = """
                INSERT INTO USERS (id_user, username, password, nama_lengkap, email, no_telepon, 
                                   program_studi, fakultas, id_role, status_aktif)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                data['id_user'], data['username'], hashed_password,
                data['nama_lengkap'], data['email'], data['no_telepon'],
                data.get('program_studi'), data.get('fakultas'), data['id_role'],
                data.get('status_aktif', 'Aktif')
            ))
            connection.commit()
            return jsonify({'success': True, 'message': 'User berhasil ditambahkan'}), 201
        except Exception as e:
            connection.rollback()
            return jsonify({'success': False, 'error': str(e)}), 400
        finally:
            cursor.close()
            connection.close()
    return jsonify({'success': False, 'error': 'Koneksi database gagal'}), 500

@users_bp.route('/api/users/<id_user>', methods=['PUT'])
@login_required
@check_role(['SPRADM'])
def update_user(id_user):
    data = request.json
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        try:
            # Cek duplikasi email (kecuali untuk user yang sedang diedit)
            cursor.execute("SELECT id_user FROM USERS WHERE email = %s AND id_user != %s", 
                           (data['email'], id_user))
            if cursor.fetchone():
                return jsonify({'success': False, 'error': 'Email sudah digunakan user lain!'}), 400

            # Siapkan field yang akan diupdate
            update_fields = {
                'nama_lengkap': data['nama_lengkap'],
                'email': data['email'],
                'no_telepon': data['no_telepon'],
                'program_studi': data.get('program_studi'),
                'fakultas': data.get('fakultas'),
                'id_role': data['id_role'],
                'status_aktif': data.get('status_aktif', 'Aktif')
            }
            
            params = list(update_fields.values())
            set_clause = ", ".join([f"{k}=%s" for k in update_fields.keys()])
            
            # PERBAIKAN: Jika password diisi, hash dan tambahkan ke query update
            if data.get('password'):
                hashed_password = generate_password_hash(data['password'])
                set_clause += ", password=%s"
                params.append(hashed_password)
                
            params.append(id_user)
            
            query = f"UPDATE USERS SET {set_clause} WHERE id_user=%s"
            cursor.execute(query, tuple(params))
            connection.commit()
            return jsonify({'success': True, 'message': 'Data user berhasil diupdate'})
        except Exception as e:
            connection.rollback()
            return jsonify({'success': False, 'error': str(e)}), 400
        finally:
            cursor.close()
            connection.close()
    return jsonify({'success': False, 'error': 'Koneksi database gagal'}), 500

@users_bp.route('/api/users/<id_user>/deactivate', methods=['POST'])
@login_required
@check_role(['SPRADM'])
def deactivate_user(id_user):
    data = request.json
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        try:
            query = """
                UPDATE USERS SET 
                    status_aktif='Nonaktif', alasan_nonaktif=%s, 
                    tgl_nonaktif=CURRENT_DATE, dinonaktifkan_oleh=%s
                WHERE id_user=%s
            """
            # PERBAIKAN: session sudah di-import di bagian atas file
            cursor.execute(query, (data['alasan'], session.get('user_id'), id_user))
            connection.commit()
            return jsonify({'success': True, 'message': 'User berhasil dinonaktifkan'})
        except Exception as e:
            connection.rollback()
            return jsonify({'success': False, 'error': str(e)}), 400
        finally:
            cursor.close()
            connection.close()
    return jsonify({'success': False, 'error': 'Koneksi database gagal'}), 500