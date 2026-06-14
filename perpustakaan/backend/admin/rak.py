from flask import Blueprint, render_template, request, jsonify
from config import get_db_connection
from backend.auth import login_required, check_role

rak_bp = Blueprint('rak', __name__)

@rak_bp.route('/')
@login_required
@check_role(['SPRADM'])
def index():
    return render_template('admin/rak.html')

@rak_bp.route('/api/rak', methods=['GET'])
@login_required
@check_role(['SPRADM'])
def get_rak():
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM RAK ORDER BY nama_rak")
        rak = cursor.fetchall()
        cursor.close()
        connection.close()
        return jsonify(rak)
    return jsonify([]), 500

@rak_bp.route('/api/rak', methods=['POST'])
@login_required
@check_role(['SPRADM'])
def create_rak():
    data = request.json
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        try:
            query = "INSERT INTO RAK (id_rak, nama_rak, lokasi_detail) VALUES (%s, %s, %s)"
            cursor.execute(query, (data['id_rak'], data['nama_rak'], data['lokasi_detail']))
            connection.commit()
            return jsonify({'success': True}), 201
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400
        finally:
            cursor.close()
            connection.close()
    return jsonify({'success': False}), 500

@rak_bp.route('/api/rak/<id_rak>', methods=['PUT'])
@login_required
@check_role(['SPRADM'])
def update_rak(id_rak):
    data = request.json
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        try:
            query = "UPDATE RAK SET nama_rak=%s, lokasi_detail=%s WHERE id_rak=%s"
            cursor.execute(query, (data['nama_rak'], data['lokasi_detail'], id_rak))
            connection.commit()
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400
        finally:
            cursor.close()
            connection.close()
    return jsonify({'success': False}), 500

@rak_bp.route('/api/rak/<id_rak>', methods=['DELETE'])
@login_required
@check_role(['SPRADM'])
def delete_rak(id_rak):
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("DELETE FROM RAK WHERE id_rak=%s", (id_rak,))
            connection.commit()
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400
        finally:
            cursor.close()
            connection.close()
    return jsonify({'success': False}), 500
