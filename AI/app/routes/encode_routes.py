from flask import Blueprint, jsonify
from ..database.db_connect import connection
import pickle
import os
import cv2
import numpy as np
import face_recognition
from firebase_admin import storage, db

client = connection()
users = client.collection("users")

# Create a blueprint for user routes
encode_bp = Blueprint('encode', __name__)

# Function to fetch image data from Firebase Storage and process it in memory
def download_image_from_firebase(blob_name):
    bucket = storage.bucket()
    blob = bucket.blob(blob_name)
    
    # Download image as a byte array
    try:
        image_bytes = blob.download_as_bytes()
    except Exception as e:
        print(f"Error downloading {blob_name}: {e}")
        return None

    # Convert byte data to numpy array
    image_np = np.frombuffer(image_bytes, np.uint8)

    # Decode the image into an OpenCV format
    img = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
    return img

# Function to generate face encodings
def find_encodings(images):
    encodeList = []
    for img in images:
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(img_rgb)
        if encodings:
            encodeList.append(encodings[0])
    return encodeList

@encode_bp.route('/generate_encodings', methods=['GET'])
def generate_encodings():
    # Fetch all image blobs from the Firebase Storage
    bucket = storage.bucket()
    blobs = bucket.list_blobs(prefix="Images/")  # Assuming images are stored in a folder called 'Images'
    
    imgList = []
    studentIds = []

    # Process each image directly in memory without downloading to disk
    for blob in blobs:
        file_name = blob.name.split('/')[-1]
        img = download_image_from_firebase(blob.name)
        if img is not None:
            imgList.append(img)
            studentIds.append(os.path.splitext(file_name)[0])

    if not imgList:
        return jsonify({"message": "No valid images found in Firebase Storage"}), 400

    # Generate encodings
    print("Generating encodings...")
    encodeListKnown = find_encodings(imgList)

    # Save the encodings and associated student IDs to a pickle file
    encodeListKnownWithIds = [encodeListKnown, studentIds]
    pickle_file_path = os.path.join(os.getcwd(), "EncodeFile.p")

    try:
        with open(pickle_file_path, 'wb') as file:
            pickle.dump(encodeListKnownWithIds, file)
        print(f"Encodings saved to {pickle_file_path}")
    except Exception as e:
        print(f"Error saving pickle file: {e}")
        return jsonify({"message": "Failed to save encoding file"}), 500

    return jsonify({"message": "Encoding complete and saved to EncodeFile.p"}), 200

@encode_bp.route("/attendance/<string:id>", methods=['GET'])
def attendance(id):
    if not id:
        return jsonify({"message": "Student ID is required"}), 400
    
    try:
        # Reference to the specific student's attendance
        student_ref = db.reference(f'Students/{id}/attendance')
        attendance_data = student_ref.get()
        
        if attendance_data is None:
            return jsonify({"message": f"No attendance data found for student ID: {id}"}), 404
        
        return jsonify({
            "id": id,
            "attendance": attendance_data
        }), 200

    except Exception as e:
        return jsonify({"message": "An error occurred", "error": str(e)}), 500


@encode_bp.route("/id", methods=['GET'])
def get_all_ids():
    try:
        # Reference to the root 'students' node
        students_ref = db.reference('Students')
        students_data = students_ref.get()
        
        if not students_data:
            return jsonify({"message": "No students found"}), 404
        
        # Extract all the keys (IDs) from the students_data
        ids = list(students_data.keys())
        
        return jsonify(ids), 200

    except Exception as e:
        return jsonify({"message": "An error occurred", "error": str(e)}), 500
