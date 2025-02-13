from flask import Blueprint, jsonify, request, g
from db_helpers import get_db_connection
import psycopg2.extras
from auth_middleware import token_required

reviews_blueprint = Blueprint('reviews_blueprint', __name__)

@reviews_blueprint.route('/books/<book_id>/reviews', methods=['POST'])
@token_required
def create_review(book_id):
    try:
        new_review_data = request.get_json()
        new_review_data["user_id"] = g.user["id"]

        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute("""
                        INSERT INTO reviews (book_id, user_id, rating, review_text)
                        VALUES (%s, %s, %s, %s)
                        RETURNING *
                        """,
                        (book_id, new_review_data['user_id'],new_review_data['rating'], new_review_data['review_text'])
        )
        created_review = cursor.fetchone()
        connection.commit()
        connection.close()
        return jsonify({"review": created_review}), 201
    except Exception as error:
        return jsonify({"error": str(error)}), 500


@reviews_blueprint.route('/books/<book_id>/reviews/<review_id>', methods=['PUT'])
@token_required
def update_review(book_id, review_id):
    try:
        updated_review_data = request.get_json()

        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute("""
                        UPDATE reviews
                        SET rating = %s, review_text = %s
                        WHERE id = %s AND book_id = %s
                        RETURNING *
                        """,
                        (updated_review_data['rating'], updated_review_data['review_text'], review_id, book_id)
        )
        updated_review = cursor.fetchone()
        connection.commit()
        connection.close()
        return jsonify({"review": updated_review}), 200
    except Exception as error:
        return jsonify({"error": str(error)}), 500
