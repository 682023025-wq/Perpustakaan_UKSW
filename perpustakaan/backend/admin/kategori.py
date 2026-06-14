from flask import Blueprint, render_template, request, jsonify
from config import get_db_connection
from backend.auth import login_required, check_role

kategori_bp = Blueprint('kategori', __name__)

@kategori_bp.route('/')
@login_required
@check_role(['SPRADM'])
def index():
    return render_template('admin/kategori.html')

@kategori_bp.route('/api/kategori', methods=['GET'])
@login_required
@check_role(['SPRADM'])
def get_kategori():
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM KATEGORI_BUKU ORDER BY nama_kategori")
        kategori = cursor.fetchall()
        cursor.close()
        connection.close()
        return jsonify(kategori)
    return jsonify([]), 500

@kategori_bp.route('/api/kategori', methods=['POST'])
@login_required
@check_role(['SPRADM'])
def create_kategori():
    data = request.json
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        try:
            query = "INSERT INTO KATEGORI_BUKU (id_kategori, nama_kategori) VALUES (%s, %s)"
            cursor.execute(query, (data['id_kategori'], data['nama_kategori']))
            connection.commit()
            return jsonify({'success': True}), 201
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400
        finally:
            cursor.close()
            connection.close()
    return jsonify({'success': False}), 500

@kategori_bp.route('/api/kategori/<int:id_kategori>', methods=['PUT'])
@login_required
@check_role(['SPRADM'])
def update_kategori(id_kategori):
    data = request.json
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        try:
            query = "UPDATE KATEGORI_BUKU SET nama_kategori=%s WHERE id_kategori=%s"
            cursor.execute(query, (data['nama_kategori'], id_kategori))
            connection.commit()
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400
        finally:
            cursor.close()
            connection.close()
    return jsonify({'success': False}), 500

@kategori_bp.route('/api/kategori/<int:id_kategori>', methods=['DELETE'])
@login_required
@check_role(['SPRADM'])
def delete_kategori(id_kategori):
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("DELETE FROM KATEGORI_BUKU WHERE id_kategori=%s", (id_kategori,))
            connection.commit()
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400
        finally:
            cursor.close()
            connection.close()
    return jsonify({'success': False}), 500
