import streamlit as st
import cv2
import os
import firebase_admin
import pickle
import datetime
import subprocess
import pandas as pd
import face_recognition
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
try:
    firebase_admin.get_app()
except ValueError:
    firebase_admin.initialize_app(cred, {
        'databaseURL' : 'https://facialattendance-d2c63-default-rtdb.firebaseio.com/',
        'storageBucket': 'facialattendance-d2c63.appspot.com'
    })
ref = db.reference('Students')
encodings_ref = db.reference('Encodings')
bucket = storage.bucket()

def main():
    st.title("Student Attendance System")
    menu = ["Store Student Details","Store Student Image","Store Encodings" ,"Take Attendance", "Check Attendance"]
    choice = st.sidebar.selectbox("Select Option", menu)

    if choice == "Store Student Details":
        store_student_details()

    elif choice == "Store Student Image":
        store_image()
    elif choice == "Store Encodings":
        store_encodings()

    elif choice == "Take Attendance":
        take_attendance()

    elif choice == "Check Attendance":
        check_attendance()

def store_student_details():
    st.subheader("Store Student Details")
    student_id = st.text_input("Student ID")
    name = st.text_input("Name")
    department = st.text_input("Department")
    joined = st.text_input("Year of Joining")
    semester = st.text_input("Semester")
    now = datetime.datetime.now()
    if st.button('Submit'):
        # Store the data in Firebase
        data = {
            'name': name,
            'department': department,
            'joined': joined,
            'total_attendance': 0,
            'semester': semester,
            'last_attendance': str(now.strftime("%Y-%m-%d %H:%M:%S"))
        }
        ref.child(student_id).set(data)

        st.success('Success! Data submitted for ' + name)

def store_image():
    st.subheader("Store Image")
    usn = st.text_input("Enter the USN of the student:")
    if st.button('Take Photo'):
        # Create the "Images" folder if it does not exist
        if not os.path.exists("Images"):
            os.makedirs("Images")
        # Initialize the webcam
        cap = cv2.VideoCapture(0)

        # Take a single photo
        while True:
            # Capture a frame from the webcam
            ret, frame = cap.read()

            # Display the frame
            cv2.imshow("Webcam", frame)

            # Check if the user pressed 'q' to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            # Check if the user clicked the left mouse button
            if cv2.waitKey(1) & 0xFF == ord(' '):  # Space bar is ASCII 32
                # Save the photo as "USN.jpg" in the "Images" folder
                file_name = f"Images/{usn}.jpg"
                cv2.imwrite(file_name, frame)
                st.write(f"Saved photo as {file_name}")

                # Upload the image to Firebase Storage
                blob = bucket.blob("Images/" + f"{usn}.jpg")

                blob.upload_from_filename(file_name)

                st.write(f"Saved photo to Firebase Storage with URL {blob.public_url}")

                break

        # Release the webcam
        cap.release()

        # Destroy all windows
        cv2.destroyAllWindows()
def store_encodings():
    st.subheader("Store Encodings")
    if st.button("Click to store encodings"):
        subprocess.run(["python", "encoding.py"])
        st.success('Success! Encodings stored.')  


def take_attendance():
    st.subheader("Take Attendance")
    if st.button("Take Attendance"):
        subprocess.run(["python", "main.py"])
    # Add code to take attendance using saved images
        st.success('Success! Attendance marked')

def get_attendance_data():
        pass
 
def check_attendance():
    st.subheader("Check Attendance")

if __name__ == '__main__':
    main()
