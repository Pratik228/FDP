# import streamlit as st
# import cv2
# import os
# def main():
#     st.title("Student Attendance System")
#     menu = ["Store Student Details","Store Student Image", "Take Attendance", "Check Attendance"]
#     choice = st.sidebar.selectbox("Select Option", menu)

#     if choice == "Store Student Details":
#         store_student_details()

#     elif choice == "Store Student Image":
#         store_image()

#     elif choice == "Take Attendance":
#         take_attendance()

#     elif choice == "Check Attendance":
#         check_attendance()
    

# def store_student_details():
#     st.subheader("Store Student Details")
#     # Add code to store student details and image

# def store_image():
#     st.subheader("Store Image")
#     # Get the USN of the student from the user
#     usn = st.text_input("Enter the USN of the student:")
#     # Create the "photos" folder if it does not exist
#     if not os.path.exists("Images"):
#         os.makedirs("Images")
#     # Initialize the webcam
#     cap = cv2.VideoCapture(0)

#     # Take a single photo
#     while True:
#         # Capture a frame from the webcam
#         ret, frame = cap.read()

#         # Display the frame
#         cv2.imshow("Webcam", frame)

#         # Check if the user pressed 'q' to quit
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

#         # Check if the user clicked the left mouse button
#         if cv2.waitKey(1) & 0xFF == ord(' '):  # Space bar is ASCII 32
#             # Save the photo as "USN.jpg" in the "photos" folder
#             file_name = f"Images/{usn}.jpg"
#             cv2.imwrite(file_name, frame)
#             st.write(f"Saved photo as {file_name}")
#             break

#     # Release the webcam
#     cap.release()

#     # Destroy all windows
#     cv2.destroyAllWindows()

# def take_attendance():
#     st.subheader("Take Attendance")
#     # Add code to take attendance using saved images

# def check_attendance():
#     st.subheader("Check Attendance")
#     # Add code to check attendance for a particular student

# if __name__ == '__main__':
#     main()
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

    # cred = credentials.Certificate("serviceAccountKey.json")
    # firebase_admin.initialize_app(cred, {
    #     'databaseURL': 'https://facialattendance-d2c63-default-rtdb.firebaseio.com/',
    #     'storageBucket': 'facialattendance-d2c63.appspot.com'
    # })
    # ref = db.reference('Encodings')

    # Load the encodings from the "EncodeFile.p" pickle file
    with open("EncodeFile.p", "rb") as f:
        encodeListKnown, studId = pickle.load(f)

    # Iterate over the images in the "Images" folder and encode them
    for image_file in os.listdir("Images"):
        image_path = os.path.join("Images", image_file)
        image_name = os.path.splitext(image_file)[0]

        # Load the image
        img = cv2.imread(image_path)

        # Convert the image from BGR to RGB
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Find the face locations in the image
        face_locations = face_recognition.face_locations(rgb_img)

        # Encode the face(s) in the image
        encodings = face_recognition.face_encodings(rgb_img, face_locations)

        if len(encodings) > 0:
            # Store the encodings in the Firebase Realtime Database
            data = {
                'encodings': encodings[0].tolist(),
                'student_id': image_name
            }
            encodings_ref.push(data)

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
