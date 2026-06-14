from flask import Blueprint, render_template, request, jsonify
from config import get_db_connection
from backend.auth import login_required, check_role

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
        cursor = connection.cursor()
        try:
            query = """
                INSERT INTO USERS (id_user, username, password, nama_lengkap, email, no_telepon, program_studi, fakultas, id_role)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                data['id_user'], data['username'], data['password'],
                data['nama_lengkap'], data['email'], data['no_telepon'],
                data.get('program_studi'), data.get('fakultas'), data['id_role']
            ))
            connection.commit()
            return jsonify({'success': True}), 201
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400
        finally:
            cursor.close()
            connection.close()
    return jsonify({'success': False}), 500

@users_bp.route('/api/users/<id_user>', methods=['PUT'])
@login_required
@check_role(['SPRADM'])
def update_user(id_user):
    data = request.json
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        try:
            query = """
                UPDATE USERS SET 
                    nama_lengkap=%s, email=%s, no_telepon=%s, 
                    program_studi=%s, fakultas=%s, id_role=%s
                WHERE id_user=%s
            """
            cursor.execute(query, (
                data['nama_lengkap'], data['email'], data['no_telepon'],
                data.get('program_studi'), data.get('fakultas'), 
                data['id_role'], id_user
            ))
            connection.commit()
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400
        finally:
            cursor.close()
            connection.close()
    return jsonify({'success': False}), 500

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
            cursor.execute(query, (data['alasan'], session.get('user_id'), id_user))
            connection.commit()
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400
        finally:
            cursor.close()
            connection.close()
    return jsonify({'success': False}), 500
