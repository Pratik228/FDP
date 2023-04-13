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


