from flask import Blueprint, jsonify, request, g
from db_helpers import get_db_connection, consolidate_reviews_in_books
import psycopg2, psycopg2.extras
from auth_middleware import token_required

books_blueprint = Blueprint('books_blueprint', __name__)






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


@books_blueprint.route('/books', methods=['GET'])
def books_index():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("""
            SELECT 
                b.id, 
                b.title, 
                b.author, 
                b.published_year, 
                b.genre, 
                b.description, 
                b.created_at, 
                b.user_id AS book_added_by_id,
                u_book.username AS added_by_username,
                r.id AS review_id, 
                r.review_text, 
                r.rating, 
                r.created_at AS review_created_at, 
                u_review.username AS reviewer_username
            FROM books b
            LEFT JOIN users u_book ON b.user_id = u_book.id 
            LEFT JOIN reviews r ON b.id = r.book_id
            LEFT JOIN users u_review ON r.user_id = u_review.id;
        """)
        books = cursor.fetchall()


        consolidated_books = consolidate_reviews_in_books(books)

        connection.commit()
        connection.close()
        return jsonify({"books": consolidated_books}), 200
    except Exception as error:
        return jsonify({"error": str(error)}), 500

@books_blueprint.route('/books/<book_id>', methods=['GET'])
def show_book(book_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("""
            SELECT 
                b.id, 
                b.title, 
                b.author, 
                b.published_year, 
                b.genre, 
                b.description, 
                b.created_at, 
                b.user_id AS book_added_by_id, 
                u_book.username AS added_by_username, 
                r.id AS review_id, 
                r.review_text, 
                r.rating, 
                r.created_at AS review_created_at, 
                u_review.username AS reviewer_username
            FROM books b
            LEFT JOIN users u_book ON b.user_id = u_book.id
            LEFT JOIN reviews r ON b.id = r.book_id
            LEFT JOIN users u_review ON r.user_id = u_review.id
            WHERE b.id = %s;""",
            (book_id,))
        
        unprocessed_book = cursor.fetchall()
        
        if unprocessed_book:
            processed_book = consolidate_reviews_in_books(unprocessed_book)[0]
            connection.close()
            return jsonify({"book": processed_book}), 200
        else:
            connection.close()
            return jsonify({"error": "Book not found"}), 404

    except Exception as error:
        return jsonify({"error": str(error)}), 500


@books_blueprint.route('/books/<book_id>', methods=['PUT'])
@token_required
def update_book(book_id):
    try:
        updated_book_data = request.json
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute("SELECT * FROM books WHERE books.id = %s", (book_id,))
        book_to_update = cursor.fetchone()
        
        if book_to_update is None:
            return jsonify({"error": "Book not found"}), 404

        if book_to_update["user_id"] is not None and book_to_update["user_id"] != g.user["id"]:
            return jsonify({"error": "Unauthorized"}), 401

        
        cursor.execute("""
            UPDATE books 
            SET title = %s, author = %s, published_year = %s, genre = %s, description = %s 
            WHERE books.id = %s 
            RETURNING *""",
            (
                updated_book_data["title"], 
                updated_book_data["author"], 
                updated_book_data["published_year"], 
                updated_book_data["genre"], 
                updated_book_data["description"], 
                book_id
            )
        )
        
        updated_book = cursor.fetchone()
        connection.commit()
        connection.close()

        return jsonify({"book": updated_book}), 200

    except Exception as error:
        return jsonify({"error": str(error)}), 500


@books_blueprint.route('/books/<book_id>', methods=['DELETE'])
@token_required
def delete_book(book_id):
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute("SELECT * FROM books WHERE id = %s", (book_id,))
        book_to_delete = cursor.fetchone()

        if book_to_delete is None:
            return jsonify({"error": "Book not found"}), 404

        if book_to_delete["user_id"] is None:
            cursor.execute("DELETE FROM books WHERE id = %s", (book_id,))
            connection.commit()
            return jsonify({"message": "Book deleted successfully"}), 200

        if book_to_delete["user_id"] != g.user["id"]:
            return jsonify({"error": "Unauthorized"}), 401

        cursor.execute("DELETE FROM books WHERE id = %s", (book_id,))
        connection.commit()

        return jsonify({"message": "Book deleted successfully"}), 200

    except Exception as error:
        return jsonify({"error": str(error)}), 500

    finally:
        if connection:
            connection.close()
