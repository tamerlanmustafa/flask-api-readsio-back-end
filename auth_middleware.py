from functools import wraps
from flask import request, jsonify, g
import jwt
import os

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        g.user = None

        authorization_header = request.headers.get('Authorization')
        if not authorization_header or not authorization_header.startswith("Bearer "):
            return jsonify({"error": "Unauthorized"}), 401
        
        try:
            token = authorization_header.split(' ')[1]
            token_data = jwt.decode(token, os.getenv('JWT_SECRET'), algorithms=["HS256"])
            if isinstance(token_data, dict) and "id" in token_data:
                g.user = token_data
            elif "payload" in token_data and isinstance(token_data["payload"], dict) and "id" in token_data["payload"]:
                g.user = token_data["payload"]
            else:
                return jsonify({"error": "Invalid token payload"}), 401

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        except Exception as error:
            return jsonify({"error": str(error)}), 500

        return f(*args, **kwargs)
    
    return decorated_function
