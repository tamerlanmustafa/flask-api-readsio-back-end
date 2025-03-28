from flask import Flask, jsonify, request, g
from flask_cors import CORS
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
CORS(app, origins=["https://readsio.netlify.app", "http://127.0.0.1:5173"])
app.register_blueprint(authentication_blueprint)
app.register_blueprint(books_blueprint)
app.register_blueprint(reviews_blueprint)


if __name__ == '__main__':
    app.run()
