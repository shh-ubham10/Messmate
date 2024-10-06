
import os
import pickle
import numpy as np
import cv2
import face_recognition
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
import numpy as np
from datetime import datetime,time

# Define time slots for meals
breakfast_time = (time(8, 0), time(9, 30))
lunch_time = (time(12, 30), time(15, 0))
dinner_time = (time(20, 0), time(22, 30))


# Firebase Setup
cred = credentials.Certificate("./assets/serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://messmate-82681-default-rtdb.firebaseio.com/",
    'storageBucket': "messmate-82681.appspot.com"
})

bucket = storage.bucket()


# Camera Setup
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

imgBackground = cv2.imread('./assets/5192479.jpg')

# Background and mode images:
folderModePath = './assets/Images'
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))



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

while True:
    success, img = cap.read()
    current_time = datetime.now().time()  # Get the current time

    # Processing each frame
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    imgBackground[162:162 + 480, 55:55 + 640] = img

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

        if counter != 0:
            if counter == 1:
                studentInfo = db.reference(f'Students/{id}').get()
                print("Stage 4 ")

                # Get the last attendance time
                last_attendance_time = datetime.strptime(studentInfo['last_attendance_time'], "%Y-%m-%d %H:%M:%S")

                # Check if the current time is within any meal period
                if is_within_time_range(current_time, *breakfast_time):
                    meal = "breakfast"
                elif is_within_time_range(current_time, *lunch_time):
                    meal = "lunch"
                elif is_within_time_range(current_time, *dinner_time):
                    meal = "dinner"
                else:
                    meal = None

                if meal:
                    # Update attendance regardless of previous status
                    print("Stage 5 ")

                    ref = db.reference(f'Students/{id}')
                    studentInfo['total_attendance'] += 1
                    ref.child('total_attendance').set(studentInfo['total_attendance'])
                    ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    print(f"Attendance marked for {meal}")

                counter += 1

            if counter >= 20:
                print("Stage 6 ")
                counter = 0
                modeType = 0
                studentInfo = []
                imgStudent = []
                imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    else:
        modeType = 0
        counter = 0

    cv2.imshow("Face Attendance", imgBackground)
    cv2.waitKey(1)
