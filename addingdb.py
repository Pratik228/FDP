
# import firebase_admin
# from firebase_admin import credentials
# from firebase_admin import db

# cred = credentials.Certificate("serviceAccountKey.json")
# firebase_admin.initialize_app(cred, {
#     'databaseURL' : 'https://facialattendance-d2c63-default-rtdb.firebaseio.com/'
# })
# ref = db.reference('Students')

# data = {
#     "1CR19CS123":{
#         "name": "Pratik Kumar Mishra",
#         "department":"CSE",
#         "joined" :"2019",
#         "total_attendance":0,
#         "semester": "8",
#         "last_attendance":"2023-03-30 00:54:34"

#     },
#         "1CR19CS030":{
#         "name": "Bhupesh Sendh",
#         "department":"CSE",
#         "joined" :"2019",
#         "total_attendance":0,
#         "semester": "8",
#         "last_attendance":"2023-03-30 00:54:34"

#     },
#         "1CR19CS152":{
#         "name": "Shantanu Hada",
#         "department":"CSE",
#         "joined" :"2019",
#         "total_attendance":0,
#         "semester": "8",
#         "last_attendance":"2023-03-30 00:54:34"

#     },
#         "1CR19IS101":{
#         "name": "Himanshu Verma",
#         "department":"ISE",
#         "joined" :"2019",
#         "total_attendance":0,
#         "semester": "8",
#         "last_attendance":"2023-03-30 00:54:34"

#     }
# }

# for key, value in data.items():
#     ref.child(key).set(value)

# from flask import Flask, request
# import firebase_admin
# from firebase_admin import credentials
# from firebase_admin import db

# cred = credentials.Certificate("serviceAccountKey.json")
# firebase_admin.initialize_app(cred, {
#     'databaseURL' : 'https://facialattendance-d2c63-default-rtdb.firebaseio.com/'
# })
# ref = db.reference('Students')

# app = Flask(__name__)

# @app.route('/', methods=['GET', 'POST'])
# def index():
#     if request.method == 'POST':
#         # Get the form data
#         student_id = request.form['student_id']
#         name = request.form['name']
#         department = request.form['department']
#         joined = request.form['joined']
#         semester = request.form['semester']

#         # Store the data in Firebase
#         data = {
#             'name': name,
#             'department': department,
#             'joined': joined,
#             'total_attendance': 0,
#             'semester': semester,
#             'last_attendance': ''
#         }
#         ref.child(student_id).set(data)
#         # ref.child('count').set(ref.get()['count'] + 1)

#        return 'Success! Data submitted for ' + name

#     return '''
#         <form method="post">
#             <label for="student_id">Student ID:</label>
#             <input type="text" id="student_id" name="student_id"><br>
#             <label for="name">Name:</label>
#             <input type="text" id="name" name="name"><br>

#             <label for="department">Department:</label>
#             <input type="text" id="department" name="department"><br>

#             <label for="joined">Year of Joining:</label>
#             <input type="text" id="joined" name="joined"><br>

#             <label for="semester">Semester:</label>
#             <input type="text" id="semester" name="semester"><br>

#             <button type="submit">Submit</button>
#         </form>
#     '''

# if __name__ == '__main__':
#     app.run()

import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
try:
    firebase_admin.get_app()
except ValueError:
    firebase_admin.initialize_app(cred, {
        'databaseURL' : 'https://facialattendance-d2c63-default-rtdb.firebaseio.com/'
    })
ref = db.reference('Students')

def add_student():
    st.write("Enter student details:")
    student_id = st.text_input("Student ID")
    name = st.text_input("Name")
    department = st.text_input("Department")
    joined = st.text_input("Year of Joining")
    semester = st.text_input("Semester")

    if st.button('Submit'):
        # Store the data in Firebase
        data = {
            'name': name,
            'department': department,
            'joined': joined,
            'total_attendance': 0,
            'semester': semester,
            'last_attendance': ''
        }
        ref.child(student_id).set(data)

        st.success('Success! Data submitted for ' + name)

if __name__ == '__main__':
    add_student()


