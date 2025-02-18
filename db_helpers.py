import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()





def get_db_connection():
    if 'ON_HEROKU' in os.environ:
        connection = psycopg2.connect(
            os.getenv('DATABASE_URL'), 
            sslmode='require'
        )
    else:
        connection = psycopg2.connect(
            host='localhost',
            database=os.getenv('POSTGRES_DATABASE'),
            user=os.getenv('POSTGRES_USERNAME'),
            password=os.getenv('POSTGRES_PASSWORD'),
            port='5432'
        )
    return connection


def consolidate_reviews_in_books(books_with_reviews):
    consolidated_books = []
    
    for book in books_with_reviews:
        book_exists = False
        for consolidated_book in consolidated_books:
            if book["id"] == consolidated_book["id"]:
                book_exists = True
                consolidated_book["reviews"].append(
                    {"review_text": book["review_text"],
                     "review_id": book["review_id"],
                     "reviewer_username": book["reviewer_username"],
                     "rating": book["rating"],
                     "review_created_at": book["review_created_at"]
                    })
                break

        if not book_exists:
            book["reviews"] = []
            if book["review_id"] is not None:
                book["reviews"].append(
                    {"review_text": book["review_text"],
                     "review_id": book["review_id"],
                     "reviewer_username": book["reviewer_username"],
                     "rating": book["rating"],
                     "review_created_at": book["review_created_at"]
                    }
                )
            del book["review_id"]
            del book["review_text"]
            del book["reviewer_username"]
            del book["rating"]
            del book["review_created_at"]
            consolidated_books.append(book)

    return consolidated_books

 
