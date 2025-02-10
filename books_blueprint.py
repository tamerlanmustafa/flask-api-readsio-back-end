from flask import Blueprint, jsonify, request, g
from db_helpers import get_db_connection
import psycopg2, psycopg2.extras
from auth_middleware import token_required

books_blueprint = Blueprint('books_blueprint', __name__)


@books_blueprint.route('/books', methods=['GET'])
def hoots_index():
    return jsonify({"message": "books index lives here"})



@books_blueprint.route('/books', methods=['POST'])
@token_required
def create_book():
    try:        
        if not g.user or "id" not in g.user:
            return jsonify({"error": "User ID missing in token"}), 401
        
        new_book = request.json
        user_id = g.user["id"] if g.user else None
        
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        if user_id:
            cursor.execute("""
                            INSERT INTO books (user_id, title, author, published_year, genre, description, created_at)
                            VALUES (%s, %s, %s, %s, %s, %s, NOW())
                            RETURNING *
                            """,
                            (user_id, new_book['title'], new_book['author'], new_book['published_year'], new_book['genre'], new_book['description'])
            )
        else:
            cursor.execute("""
                            INSERT INTO books (title, author, published_year, genre, description, created_at)
                            VALUES (%s, %s, %s, %s, %s, NOW())
                            RETURNING *
                            """,
                            (new_book['title'], new_book['author'], new_book['published_year'], new_book['genre'], new_book['description'])
            )
        
        created_book = cursor.fetchone()
        connection.commit()
        connection.close()

        return jsonify({"book": created_book}), 201
    except Exception as error:
        return jsonify({"error": str(error)}), 500




