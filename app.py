from flask import Flask, jsonify, request, g
from dotenv import load_dotenv
import os
import jwt
import psycopg2, psycopg2.extras
import bcrypt
from auth_middleware import token_required
from auth_blueprint import authentication_blueprint
from books_blueprint import books_blueprint
from reviews_blueprint import reviews_blueprint


load_dotenv()


app = Flask(__name__)

@app.after_request
def add_cors_headers(response):
    allowed_origins = ['https://readsio.netlify.app', 'http://localhost:5173']
    origin = request.headers.get('Origin')
    if origin in allowed_origins:
        response.headers.add('Access-Control-Allow-Origin', origin)
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
    return response


app.register_blueprint(authentication_blueprint)
app.register_blueprint(books_blueprint)
app.register_blueprint(reviews_blueprint)


if __name__ == '__main__':
    app.run()
