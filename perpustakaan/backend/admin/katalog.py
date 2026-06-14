from flask import Blueprint, render_template, request, jsonify
from config import get_db_connection
from backend.auth import login_required, check_role

katalog_bp = Blueprint('katalog', __name__)

@katalog_bp.route('/')
@login_required
@check_role(['SPRADM'])
def index():
    return render_template('admin/katalog.html')

@katalog_bp.route('/api/katalog', methods=['GET'])
@login_required
@check_role(['SPRADM'])
def get_katalog():
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT k.*, kb.nama_kategori
            FROM KATALOG_BUKU k
            JOIN KATEGORI_BUKU kb ON k.id_kategori = kb.id_kategori
            ORDER BY k.judul
        """
        cursor.execute(query)
        katalog = cursor.fetchall()
        cursor.close()
        connection.close()
        return jsonify(katalog)
    return jsonify([]), 500

@katalog_bp.route('/api/katalog', methods=['POST'])
@login_required
@check_role(['SPRADM'])
def create_katalog():
    data = request.json
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        try:
            query = """
                INSERT INTO KATALOG_BUKU (isbn, judul, pengarang, penerbit, tahun_terbit, sinopsis, bahasa, jumlah_halaman, url_cover, id_kategori)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                data['isbn'], data['judul'], data['pengarang'],
                data['penerbit'], data['tahun_terbit'], data.get('sinopsis'),
                data['bahasa'], data['jumlah_halaman'], data.get('url_cover'),
                data['id_kategori']
            ))
            connection.commit()
            return jsonify({'success': True}), 201
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400
        finally:
            cursor.close()
            connection.close()
    return jsonify({'success': False}), 500

@katalog_bp.route('/api/katalog/<isbn>', methods=['PUT'])
@login_required
@check_role(['SPRADM'])
def update_katalog(isbn):
    data = request.json
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        try:
            query = """
                UPDATE KATALOG_BUKU SET 
                    judul=%s, pengarang=%s, penerbit=%s, tahun_terbit=%s,
                    sinopsis=%s, bahasa=%s, jumlah_halaman=%s, url_cover=%s, id_kategori=%s
                WHERE isbn=%s
            """
            cursor.execute(query, (
                data['judul'], data['pengarang'], data['penerbit'],
                data['tahun_terbit'], data.get('sinopsis'), data['bahasa'],
                data['jumlah_halaman'], data.get('url_cover'),
                data['id_kategori'], isbn
            ))
            connection.commit()
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400
        finally:
            cursor.close()
            connection.close()
    return jsonify({'success': False}), 500

@katalog_bp.route('/api/katalog/<isbn>', methods=['DELETE'])
@login_required
@check_role(['SPRADM'])
def delete_katalog(isbn):
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("DELETE FROM KATALOG_BUKU WHERE isbn=%s", (isbn,))
            connection.commit()
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400
        finally:
            cursor.close()
            connection.close()
    return jsonify({'success': False}), 500
