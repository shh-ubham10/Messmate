from flask import Blueprint, request, jsonify,current_app
from ..database.db_connect import connection

client = connection()
users= client.collection("users")  # Database

# Create a blueprint for user routes
user_bp = Blueprint('user', __name__)


# Get users

@user_bp.route('/users', methods=['GET'])
def get_all_users():
    # Fetch all users from Firestore
    all_users_query = users.stream()

    # Convert Firestore query results to a list of dictionaries (excluding password fields)
    all_users = [
        {**user.to_dict(), 'id': user.id} for user in all_users_query
        if 'password' in user.to_dict() and 'cpassword' in user.to_dict()  # Exclude password fields
    ]

    # Check if users list is empty
    if not all_users:
        return jsonify({'message': 'No users found'}), 400

    return jsonify(all_users), 200


# Get a single user by email

@user_bp.route('/users/<email>', methods=['GET'])
def get_one_user(email):
    if not email:
        return jsonify({'message': 'Email is required'}), 400
    
    # Query Firestore for the user by email
    user_query = users.where('email', '==', email).limit(1).stream()
    
    # Get the first result
    user = next(user_query, None)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404  # Changed status code for not found
    
    # Convert the Firestore document to a dictionary
    user_data = user.to_dict()
    # Exclude sensitive fields
    if 'password' in user_data:
        del user_data['password']
    if 'cpassword' in user_data:
        del user_data['cpassword']
    
    return jsonify(user_data), 200

# Create a user

@user_bp.route('/users', methods=['POST'])
def create_user():
    bcrypt = current_app.config['bcrypt']  # Access bcrypt instance here

    # Get user data from the request
    data = request.json
    regNo = data.get('regNo')
    name = data.get('name')
    email = data.get('email')
    mobileno = data.get('mobileno')
    role = data.get('role')
    password = data.get('password')
    cpassword = data.get('cpassword')

    # Validate password and confirm password
    if password != cpassword:
        return jsonify({'message': 'Passwords do not match'}), 400

    # Check for duplicate user (Firestore query)
    user_query = users.where('email', '==', email).stream()
    duplicate_user = next(user_query, None)  # Get the first result or None

    if duplicate_user:
        return jsonify({'message': 'User already exists'}), 409

    # Hash the password using bcrypt
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    # Insert new user into Firestore
    user_object = {
        'name': name,
        'email': email,
        'mobileno': mobileno,
        'role': role,
        'password': hashed_password,
        'cpassword': hashed_password,
        'regNo': regNo
    }

    users.add(user_object)  # Firestore add method for inserting a new document
    return jsonify({'message': f'User {email} created successfully'}), 201

# Get a user by Id
@user_bp.route('/user/<int:regNo>', methods=['GET'])
def get_user(regNo):
    if not regNo:
        return jsonify({'message': 'User ID Required'}), 400

    # Query Firestore for the user by regNo
    user_query = users.where('regNo', '==', regNo).limit(1).stream()

    # Get the first result
    user = next(user_query, None)

    if not user:
        return jsonify({'message': 'No users found'}), 404  # Changed to 404 for not found

    # Convert the Firestore document to a dictionary
    user_data = user.to_dict()
    # Exclude sensitive fields
    user_data.pop('password', None)  # Removes 'password' if it exists
    user_data.pop('cpassword', None)  # Removes 'cpassword' if it exists

    return jsonify(user_data), 200



# Update user
@user_bp.route('/updateUser/<string:uid>', methods=['PUT'])
def update_user(uid):
    data = request.json
    name = data.get('name')
    email = data.get('email')
    mobileno = data.get('mobileno')
    role = data.get('role')

    if not uid:
        return jsonify({'message': 'User ID is required'}), 400

    # Query Firestore for the user by the auto-generated document ID
    user_ref = users.document(uid)  # Use the document ID
    user = user_ref.get()

    if not user.exists:
        return jsonify({'message': 'User not found'}), 404

    # Convert Firestore document to dictionary
    user_data = user.to_dict()

    # Check for duplicates (email or mobileno)
    duplicate_query = users.where('email', '==', email).where('mobileno', '==', mobileno).limit(1).stream()
    duplicate_user = next(duplicate_query, None)

    if duplicate_user and duplicate_user.id != uid:  # Check if duplicate ID is not the same as the current user ID
        return jsonify({'message': 'Duplicate email or mobileno found'}), 409

    # Update user fields
    updated_object = {
        'name': name,
        'email': email,
        'mobileno': mobileno,
        'role': role
    }

    # Update the user in Firestore
    user_ref.update(updated_object)

    return jsonify({'message': f'User {email} updated successfully'}), 200

# reset password
@user_bp.route('/resetPassword', methods=['POST'])
def reset_password():
    # Get the request data
    bcrypt = current_app.config['bcrypt']  
    data = request.json
    email = data.get('email')
    oldpassword = data.get('oldpassword')
    newpassword = data.get('newpassword')

    if not email or not oldpassword or not newpassword:
        return jsonify({'message': 'Missing required fields'}), 400

    # Find user by email
    user_query = users.where('email', '==', email).limit(1).stream()
    user_doc = next(user_query, None)

    if not user_doc:
        return jsonify({'message': 'User not available'}), 404

    user_data = user_doc.to_dict()

    # Check if old password matches
    match_passwd = bcrypt.check_password_hash(user_data['password'], oldpassword)

    if not match_passwd:
        return jsonify({'message': 'Unauthorized'}), 401

    # Hash the new password
    hashed_password = bcrypt.generate_password_hash(newpassword).decode('utf-8')

    # Update password in Firestore
    updated_data = {'password': hashed_password, 'cpassword': hashed_password}
    users.document(user_doc.id).update(updated_data)

    return jsonify({'message': 'Password reset successfully'}), 200

#delete user
@user_bp.route('/delete/<string:email>', methods=['DELETE'])
def delete_user(email):
    if not email:
        return jsonify({'message': 'Email is required'}), 400

    # Query Firestore for the user by email
    user_query = users.where('email', '==', email).limit(1).stream()
    user_doc = next(user_query, None)

    # Check if user exists
    if not user_doc:
        return jsonify({'message': 'User not found'}), 404

    # Delete the user
    users.document(user_doc.id).delete()

    return jsonify({'message': f'User {email} deleted successfully'}), 200

@user_bp.route('/', methods=['GET'])
def index():
    return jsonify({'message': 'Welcome to the user API'}), 200