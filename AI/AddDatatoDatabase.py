import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("./assets/serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://messmate-82681-default-rtdb.firebaseio.com/"
})

ref = db.reference('Students')

data = {

    "10321210134":
        {
            "name": "Satvik Manchanda",
            "major": "Robotics",
            "starting_year": 2017,
            "total_attendance": 7,
            "standing": "G",
            "year": 4,
            "last_attendance_time": "2021-7-7 00:54:34"
        },
            "10321210138":
        {
            "name": "Nikola Tesla",
            "major": "Electrical",
            "starting_year": 2014,
            "total_attendance": 9,
            "standing": "G",
            "year": 4,
            "last_attendance_time": "2018-7-7 00:54:34"
        },

         "11721210009":
        {
            "name": "Lokesh Kumar",
            "major": "Computer science",
            "starting_year": 2019,
            "total_attendance": 5,
            "standing": "G",
            "year": 4,
            "last_attendance_time": "2024-7-7 00:54:34"
        },
                 "10321210121":
        {
            "name": "Anurag Goyal",
            "major": "Computer science",
            "starting_year": 2019,
            "total_attendance": 5,
            "standing": "G",
            "year": 4,
            "last_attendance_time": "2024-7-7 00:54:34"
        },
        "10321210144":{
            "name":"Rakesh",
            "major":"Computer science",
            "starting_year":2019,
            "total_attendance":5,
            "standing":"G",
            "year":4,
            "last_attendance_time":"2024-7-7 00:54:34"
        }
        
}

for key, value in data.items():
    ref.child(key).set(value)