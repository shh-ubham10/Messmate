from io import BytesIO
from PIL import Image
import os
import pickle
import numpy as np
import cv2
import face_recognition
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
import numpy as np
from datetime import datetime,time
import requests

# Define time slots for meals
breakfast_time = (time(8, 0), time(9, 30))
lunch_time = (time(10, 30), time(14, 0))
snack_time = (time(17,0), time(20,5))
dinner_time = (time(20, 20), time(23, 30))


# Firebase Setup
cred = credentials.Certificate("./assets/serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://messmate-82681-default-rtdb.firebaseio.com/",
    'storageBucket': "messmate-82681.appspot.com"
})

bucket = storage.bucket()


# Camera Setup
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 680)


# Background and mode images:

blob_list = bucket.list_blobs(prefix='Images/')

imgModeList = []

for blob in blob_list:
    # Get the download URL for each blob
    url = blob.public_url

    # Download the image using requests
    response = requests.get(url)
    img_array = np.asarray(bytearray(response.content), dtype=np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    imgModeList.append(img)



# Load the encoding file
print("Loading Encode File ...")
file = open('EncodeFile.p', 'rb')
encodeListKnownWithIds = pickle.load(file)
file.close()



encodeListKnown, studentIds = encodeListKnownWithIds
print("Encode File Loaded")

modeType = 0
counter = 0
id = -1
imgStudent = []

def is_within_time_range(current_time, start_time, end_time):
    return start_time <= current_time <= end_time

def get_meal_slot(current_time):
    if is_within_time_range(current_time, *breakfast_time):
        return 0  # Breakfast
    elif is_within_time_range(current_time, *lunch_time):
        return 1  # Lunch
    elif is_within_time_range(current_time, *snack_time):
        return 2  # Snack
    elif is_within_time_range(current_time, *dinner_time):
        return 3  # Dinner
    return None  # Not in meal time


# Add a dictionary to track whether attendance is already marked for a student during a specific meal slot
marked_attendance = {}

while True:
    success, img = cap.read()
    current_time = datetime.now().time()  # Get the current time
    current_date = datetime.now().strftime("%d-%m-%Y")  # Format the current date as "DD-MM-YYYY"

    # Processing each frame
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)


    if faceCurFrame:
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)

            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:
                id = studentIds[matchIndex]

                if counter == 0:
                    counter = 1
                    modeType = 1

            # Draw rectangle around the detected face
            top, right, bottom, left = faceLoc
            top, right, bottom, left = top * 4, right * 4, bottom * 4, left * 4  # since imgS is resized to 0.25
            cv2.rectangle(img, (left + 55, top + 162), (right + 55, bottom + 162), (0, 255, 0), 2)

            # Display student ID above the rectangle
            text_position = (left + 55, top + 162 - 10)  # Position above the top-left corner of the rectangle
            cv2.putText(img, f"ID: {id}", text_position, cv2.FONT_HERSHEY_SIMPLEX, 
                        1, (255, 255, 255), 2)  # Font size 1, white color, thickness 2

        if counter != 0:
            if counter == 1:
                studentInfo = db.reference(f'Students/{id}').get()

                # Get attendance data for the current day
                attendance_ref = db.reference(f'Students/{id}/attendance/{current_date}')
                attendance_record = attendance_ref.get()

                # If no record exists for the day, create a new one
                if attendance_record is None:
                    attendance_record = ["A", "A", "A", "A"]  # Default to 'A' for all meals

                # Determine the current meal slot (breakfast, lunch, dinner)
                meal_slot = get_meal_slot(current_time)

                if meal_slot is not None:
                    # Check if the student already marked in this meal slot
                    if marked_attendance.get(id, {}).get(meal_slot, False):
                        print(f"Attendance already marked for meal slot {meal_slot} for {id}")
                    else:
                        # Mark the current meal slot as 'P' (Present)
                        attendance_record[meal_slot] = "P"

                        # Update the attendance for the day in Firebase
                        attendance_ref.set(attendance_record)

                        print(f"Attendance marked for meal slot {meal_slot} for {id}")

                        # Set the marked flag to True for this student and meal slot
                        if id not in marked_attendance:
                            marked_attendance[id] = {}
                        marked_attendance[id][meal_slot] = True

                counter += 1

            if counter >= 20:
                counter = 0
                
    else:
        counter = 0

    cv2.imshow("Face Attendance", img)
    cv2.waitKey(1)
