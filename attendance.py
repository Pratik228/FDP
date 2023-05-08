import streamlit as st
import cv2
import os
import firebase_admin
import base64
import pickle
import datetime
import subprocess
import pandas as pd
import face_recognition
import numpy as np
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from firebase_config import initialize_firebase
from utils import load_known_encodings_and_ids
from webcam_capture import webcam_capture
import pytz

bucket, ref, encodings_ref = initialize_firebase()

local_tz = pytz.timezone('Asia/Kolkata')
            
def main():
    # st.title("Student Attendance System")
    menu = ["Home","Store Student Details","Store Student Image","Store Encodings" ,"Take Attendance", "Check Attendance"]
    choice = st.sidebar.selectbox("Select Option", menu)

    if choice == "Home":
        st.markdown(f"""
            <style>
                body {{
                    background: linear-gradient(90deg, rgba(2,0,36,1) 0%, rgba(119,9,121,1) 35%, rgba(0,212,255,1) 100%);
                    font-family: 'Arial', sans-serif;
                }}
                .home-text {{
                    font-size: 40px;
                    font-weight: bold;
                    text-align: center;
                    color: white;
                    padding: 20px;
                }}
            </style>
        """, unsafe_allow_html=True)

        st.markdown("<div class='home-text'>Welcome to the Student Attendance System</div>", unsafe_allow_html=True)
        st.markdown("<div class='home-text'>Please select an option from the sidebar to get started.</div>", unsafe_allow_html=True)

    elif choice == "Store Student Details":
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
    section = st.text_input("Section")
    now = datetime.datetime.now(local_tz)
    if st.button('Submit'):
        # Store the data in Firebase
        data = {
            'name': name,
            'department': department,
            'joined': joined,
            'total_attendance': 0,
            'semester': semester,
            'section': section,
            'last_attendance': str(now.strftime("%Y-%m-%d %H:%M:%S"))
        }
        ref.child(student_id).set(data)

        st.success('Success! Data submitted for ' + name)
#  Original one
# def store_image():
#     st.subheader("Store Image")
#     usn = st.text_input("Enter the USN of the student:")
#     if st.button('Take Photo'):
#         # Create the "Images" folder if it does not exist
#         if not os.path.exists("Images"):
#             os.makedirs("Images")
#         # Initialize the webcam
#         cap = cv2.VideoCapture(0)

#         # Take a single photo
#         while True:
#             # Capture a frame from the webcam
#             ret, frame = cap.read()

#             # Display the frame
#             cv2.imshow("Webcam", frame)

#             # Check if the user pressed 'q' to quit
#             if cv2.waitKey(1) & 0xFF == ord('q'):
#                 break

#             # Check if the user clicked the left mouse button
#             if cv2.waitKey(1) & 0xFF == ord(' '):  # Space bar is ASCII 32
#                 # Save the photo as "USN.jpg" in the "Images" folder
#                 file_name = f"Images/{usn}.jpg"
#                 cv2.imwrite(file_name, frame)
#                 st.write(f"Saved photo as {file_name}")

#                 # Upload the image to Firebase Storage
#                 blob = bucket.blob("Images/" + f"{usn}.jpg")

#                 blob.upload_from_filename(file_name)

#                 st.write(f"Saved photo to Firebase Storage with URL {blob.public_url}")

#                 break

#         # Release the webcam
#         cap.release()

#         # Destroy all windows
#         cv2.destroyAllWindows()

# Giving options to the users
def store_image():
    st.subheader("Store Image")
    option = st.radio("Enter USN first then Select Option", ("Upload Image", "Take Photo", "Capture from Web"))
    usn = st.text_input("Enter the USN of the student:")
    if option == "Upload Image":
        
        uploaded_file = st.file_uploader("Choose an image file", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            file_name = f"Images/{usn}.jpg"
            with open(file_name, "wb") as f:
                f.write(uploaded_file.read())
            st.write(f"Saved photo as {file_name}")
            # Upload the image to Firebase Storage
            blob = bucket.blob("Images/" + f"{usn}.jpg")
            blob.upload_from_filename(file_name)
            st.write(f"Saved photo to Firebase Storage with URL {blob.public_url}")
    elif option == "Take Photo":
        # usn = st.text_input("Enter the USN of the student:")
        # Create the "Images" folder if it does not exist
        if not os.path.exists("Images"):
            os.makedirs("Images")
        # Initialize the webcam
        cap = cv2.VideoCapture(0)
        st.write("Please look at the camera and come a little closer. The camera will automatically capture your photo once your face is properly detected.")

        # Take a single photo
        while True:
            # Capture a frame from the webcam
            ret, frame = cap.read()

            # Resize image for faster processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

            # Detect faces in the frame
            face_locations = face_recognition.face_locations(small_frame)

            # If a face is detected, capture the photo
            if len(face_locations) == 1:
                file_name = f"Images/{usn}.jpg"
                cv2.imwrite(file_name, frame)
                st.write(f"Saved photo as {file_name}")

                # Upload the image to Firebase Storage
                blob = bucket.blob("Images/" + f"{usn}.jpg")
                blob.upload_from_filename(file_name)
                st.write(f"Saved photo to Firebase Storage with URL {blob.public_url}")

                break

            # Check if the user pressed 'q' to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
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

#  Old one changing it completely
# def take_attendance():
#     st.subheader("Take Attendance")
#     if st.button("Take Attendance"):
#         subprocess.run(["python", "main.py"])
#     # Add code to take attendance using saved images
#         st.success('Success! Attendance marked')

# New one with enhanced options
import dlib
def _css_to_rect(css):
    return dlib.rectangle(css.left(), css.top(), css.right(), css.bottom())

def take_attendance():
    st.subheader("Take Attendance")
    semester = st.selectbox("Select Semester", options=[1, 2, 3, 4, 5, 6, 7, 8])
    section = st.selectbox("Select Section", options=["A", "B", "C", "D"])
    option = st.radio("Select Option", ("Live Video", "Upload Image"))
    if option == "Live Video":
        if st.button("Take Attendance"):
            subprocess.run(["python", "main.py"])
            st.success('Success! Attendance marked')
    elif option == "Upload Image":
        uploaded_file = st.file_uploader("Choose an image file", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            # Read in the uploaded image
            file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

            # Resize image for faster processing
            img = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)


            # Detect faces in the image
            face_locations = face_recognition.face_locations(img)
            face_encodings = face_recognition.face_encodings(img, face_locations)

            # Load known encodings and student IDs
            encodeKnown, studId = load_known_encodings_and_ids()

            # Loop through each face encoding detected in the uploaded image
            marked_students = 0
            for face_encoding in face_encodings:
                # Find the closest matching known encoding
                distances = face_recognition.face_distance(encodeKnown, face_encoding)
                min_distance_index = np.argmin(distances)
                min_distance = distances[min_distance_index]

                # Set a threshold for the minimum distance to consider a match
                threshold = 0.6

                # If the minimum distance is below the threshold, mark attendance
                if min_distance < threshold:
                    id = studId[min_distance_index]
                    studentInfo = db.reference(f'Students/{id}').get()
                    if studentInfo is not None:
                        datetimeObject = datetime.datetime.strptime(studentInfo['last_attendance'], '%Y-%m-%d %H:%M:%S').replace(tzinfo=local_tz)
                        secondsElapsed = (datetime.datetime.now(local_tz) - datetimeObject).total_seconds()

                        if secondsElapsed > 30:
                            ref = db.reference(f'Students/{id}')
                            studentInfo['total_attendance'] += 1
                            ref.child('total_attendance').set(studentInfo['total_attendance'])
                            ref.child('last_attendance').set(datetime.datetime.now(local_tz).strftime("%Y-%m-%d %H:%M:%S"))
                            marked_students += 1
                        else:
                            st.warning(f"{studentInfo['name']}'s attendance was already marked within the last 30 seconds.")
                    else:
                        st.warning(f"No student found with ID {id}.")

            if marked_students == 0:
                st.warning("No matching faces found in the uploaded image.")
            else:
                st.success(f"Attendance marked for {marked_students} students.")
    st.subheader("Manual Attendance")
    st.write("Mark attendance for students who were not detected:")
    if st.button("Load Unmarked Students"):
        # Get the attendance data from the "Students" node in the Firebase database
        attendance_ref = db.reference('Students')
        attendance_data = attendance_ref.get()
        # attendance_df = pd.DataFrame.from_dict(attendance_data, orient='index')
        attendance_df = pd.DataFrame.from_dict(attendance_data, orient='index')
        attendance_df = attendance_df[(attendance_df['semester'] == str(semester)) & (attendance_df['section'] == section)]


        # Get the last attendance date and time from the "last_attendance" column
        last_attendance = attendance_df["last_attendance"]

        # Check if the last attendance date matches today's date
        today = datetime.datetime.now(local_tz).strftime("%Y-%m-%d")
        absent_students = []
        for i, date_time in last_attendance.items():
            date = date_time.split(" ")[0]
            if date != today:
                absent_students.append(i)
        ############## For Testing purpose ###################### 
        # for i, date_time in last_attendance.items():
        #     datetimeObject = datetime.datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S').replace(tzinfo=local_tz)
        #     secondsElapsed = (datetime.datetime.now(local_tz) - datetimeObject).total_seconds()
        #     if secondsElapsed > 30:
        #         absent_students.append(i)


        # Show the list of students who were not marked present today and use checkboxes
        students_to_mark = {}
        if len(absent_students) > 0:
            st.write("Students not marked present today:")
            for usn in absent_students:
                students_to_mark[usn] = st.checkbox(f"{usn}: {attendance_data[usn]['name']}")

            # Provide an option to mark attendance manually
            if st.button("Mark Attendance"):
                for usn, mark_attendance in students_to_mark.items():
                    if mark_attendance:
                        studentInfo = db.reference(f'Students/{usn}').get()
                        if studentInfo is not None:
                            ref = db.reference(f'Students/{usn}')
                            studentInfo['total_attendance'] += 1
                            ref.child('total_attendance').set(studentInfo['total_attendance'])
                            ref.child('last_attendance').set(datetime.datetime.now(local_tz).strftime("%Y-%m-%d %H:%M:%S"))
                            st.success(f"Attendance marked for {studentInfo['name']}")
                        else:
                            st.warning(f"No student found with USN {usn}.")
        else:
            st.success("All students are marked present today.")

 
def check_attendance():
    st.subheader("Check Attendance")
    # Get the attendance data from the "Students" node in the Firebase database
    semester = st.selectbox("Select Semester", options=[1, 2, 3, 4, 5, 6, 7, 8])
    section = st.selectbox("Select Section", options=["A", "B", "C", "D"])

    attendance_ref = db.reference('Students')
    attendance_data = attendance_ref.get()

    # Create a pandas dataframe from the attendance data
    # attendance_df = pd.DataFrame.from_dict(attendance_data, orient='index')
    attendance_df = pd.DataFrame.from_dict(attendance_data, orient='index')
    attendance_df = attendance_df[(attendance_df['semester'] == str(semester)) & (attendance_df['section'] == section)]


    # Get the last attendance date and time from the "last_attendance" column
    last_attendance = attendance_df["last_attendance"]
    present_today = 0

    # Check if the last attendance date matches today's date
    today = datetime.datetime.now(local_tz).strftime("%Y-%m-%d")
    for i, date_time in last_attendance.items():
        date = date_time.split(" ")[0]
        if date == today:
            present_today += 1

    # Display the attendance data in a table
    st.dataframe(attendance_df)

    # Display a message indicating the number of students present today
    if present_today == 0:
        st.warning("No students are present today.")
    else:
        # st.success(f"{present_today} students are present today!")
        st.success(f"{present_today} students are present in section {section} today!")

    # Create a button to download the CSV file
    csv = attendance_df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="attendance.csv">Download CSV file</a>'
    # st.markdown(href, unsafe_allow_html=True)
    st.download_button(label="Download CSV file", data=csv, file_name=f"attendance_{today}.csv", mime="text/csv")


if __name__ == '__main__':
    main()
