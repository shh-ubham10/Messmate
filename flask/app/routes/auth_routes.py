import jwt
import bcrypt
from flask import Blueprint, request, jsonify, current_app, make_response
from ..database.db_connect import connection
import os
from functools import wraps
from datetime import datetime, timedelta

client = connection()
users= client.collection("users") 

# Create a blueprint for user routes
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'All fields are required'}), 400

    # Query Firestore for the user by email
    user_query = users.where('email', '==', email).limit(1).stream()
    user = next(user_query, None)

    if not user:
        return jsonify({'message': 'User not available'}), 401

    user_data = user.to_dict()

    # Check password
    if not bcrypt.checkpw(password.encode('utf-8'), user_data['password'].encode('utf-8')):
        return jsonify({'message': 'Unauthorized'}), 401

    # Generate tokens
    user_info = {
        "name": user_data['name'],
        "email": user_data['email'],
        "role": user_data['role'],
        "mobileno": user_data['mobileno']
    }

    # Generate access token
    access_token = jwt.encode({
        "UserInfo": user_info,
        "exp": datetime.utcnow() + timedelta(minutes=15)
    }, os.getenv('AUTH_TOKEN'), algorithm="HS256")

    # Generate refresh token
    refresh_token = jwt.encode({
        "useremail": user_data['email'],
        "exp": datetime.utcnow() + timedelta(days=7)
    }, os.getenv('AUTH_TOKEN'), algorithm="HS256")

    # Set refresh token in HttpOnly cookie
    response = make_response(jsonify({
        'userId': user.id,
        'name': user_data['name'],
        'email': user_data['email'],
        'mobileno': user_data['mobileno'],
        'role': user_data['role'],
        'accessToken': access_token
    }))
    response.set_cookie('jwt', refresh_token, httponly=True, max_age=7*24*60*60)

    return response


# Helper function for verifying JWT and handling errors
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        cookies = request.cookies
        if not cookies or 'jwt' not in cookies:
            return jsonify({'message': 'Unauthorized: no cookie store'}), 401

        token = cookies.get('jwt')
        try:
            decoded_token = jwt.decode(token, os.getenv('AUTH_TOKEN'), algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 403
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Forbidden: invalid token'}), 403

        return f(decoded_token, *args, **kwargs)
    
    return decorated

# Refresh route
@auth_bp.route('/refresh', methods=['POST'])
@token_required
def refresh(decoded_token):
    email = decoded_token.get('useremail')
    if not email:
        return jsonify({'message': 'Unauthorized: no user email found in token'}), 401

    # Query Firestore for the user by email
    user_query = users.where('email', '==', email).limit(1).stream()
    user = next(user_query, None)

    if not user:
        return jsonify({'message': 'Unauthorized: no user found'}), 401

    user_data = user.to_dict()

    # Generate new access token
    access_token = jwt.encode({
        "UserInfo": {
            "useremail": user_data['email'],
            "role": user_data['role']
        },
        "exp": datetime.utcnow() + timedelta(minutes=15)
    }, os.getenv('AUTH_TOKEN'), algorithm="HS256")

    # Return updated user info and access token
    response = {
        'userId': user.id,
        'name': user_data['name'],
        'email': user_data['email'],
        'mobileno': user_data['mobileno'],
        'role': user_data['role'],
        'accessToken': access_token
    }

    return jsonify(response), 200

# Logout 
@auth_bp.route('/logout', methods=['POST'])
def logout():
    # Get cookies from the request
    cookies = request.cookies

    # Check if the jwt cookie exists
    if not cookies.get('jwt'):
        return '', 204  # No Content (Already logged out or no token)

    # Clear the jwt cookie by setting its expiry to 0
    response = make_response(jsonify({'message': 'Logout Successfully'}))
    response.set_cookie('jwt', '', expires=0, httponly=True, samesite='None', secure=True)

    return response


@auth_bp.route('/', methods=['GET'])
def index():
    return jsonify({'message': 'Welcome to the user API'}), 200