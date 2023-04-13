import cv2
import os
import numpy as np
import pickle
import cvzone
import face_recognition
import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL' : 'https://facialattendance-d2c63-default-rtdb.firebaseio.com/',
    'storageBucket' : 'facialattendance-d2c63.appspot.com'
    })

bucket = storage.bucket()
# open default camera (index 0)
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)
imgBackground = cv2.imread('Resources/background.png')

# Importing images to list
folderModePath = 'Resources/Modes'
modePath = os.listdir(folderModePath)
imgModeList = []
for path in modePath:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))
#import the encoding file
file = open('EncodeFile.p', 'rb')
encodeKnownwithIds = pickle.load(file)
file.close()
encodeKnown, studId = encodeKnownwithIds
#print(studId)
datetimeObject = str(datetime.datetime.now())
modeType = 0
counter = 0
id=-1
while True:
    # read a frame from the camera
    ret, frame = cap.read()
    imgS = cv2.resize(frame, (0,0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)


    imgBackground[162:162+480, 55:55+640] = frame
    imgBackground[44:44+633, 808:808+414] = imgModeList[modeType]
    if faceCurFrame:
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeKnown, encodeFace)

            print("matches", matches)
            print("faceDis", faceDis)

            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:
                print("Face Detected")
                print(studId[matchIndex])
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
                bbox = 55+x1, 162+y1, x2-x1, y2-y1 
                imgBackground = cvzone.cornerRect(imgBackground, bbox)
                id = studId[matchIndex]
                if counter==0:
                    cvzone.putTextRect(imgBackground, "Loading", (275, 400))
                    cv2.imshow("Face Attendance", imgBackground)
                    cv2.waitKey(1)
                    counter=1
                    modeType=1
        if counter!=0:
            if counter ==1:
                studentInfo = db.reference(f'Students/{id}').get()
                print(studentInfo)
                 # Get the Image from the storage
                blob = bucket.get_blob(f'Images/{id}.jpg')
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)
                 # Update data of attendance
                if studentInfo is not None:
                    datetimeObject = datetime.datetime.strptime(studentInfo['last_attendance'], '%Y-%m-%d %H:%M:%S')
                # datetimeObject = datetime.datetime.strptime(studentInfo['last_attendance'],
                #                                    "%Y-%m-%d %H:%M:%S")
                secondsElapsed = (datetime.datetime.now() - datetimeObject).total_seconds()
                print(secondsElapsed)
                if secondsElapsed > 30:
                    ref = db.reference(f'Students/{id}')
                    studentInfo['total_attendance'] += 1
                    ref.child('total_attendance').set(studentInfo['total_attendance'])
                    ref.child('last_attendance').set(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    modeType = 3
                    counter = 0
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
            if modeType != 3:
 
                if 10 < counter < 20:
                    modeType = 2
 
                imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
 
                if counter <= 10:
                    cv2.putText(imgBackground, str(studentInfo['total_attendance']), (861, 125),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(studentInfo['department']), (1006, 550),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(id), (1006, 493),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(studentInfo['semester']), (1025, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(studentInfo['joined']), (1125, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
 
                    (w, h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                    offset = (414 - w) // 2
                    cv2.putText(imgBackground, str(studentInfo['name']), (808 + offset, 445),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)
 
                    # imgBackground[175:175 + 216, 909:909 + 216] = imgStudent
 
                counter += 1
 
                if counter >= 20:
                    counter = 0
                    modeType = 0
                    studentInfo = []
                    imgStudent = []
                    # imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
    else:
        modeType = 0
        counter = 0
    # display the captured frame
    # cv2.imshow('Webcam', frame)
    cv2.imshow('Face Attendance', imgBackground)
    # wait for the user to press 'q' key to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# release the camera and close the window
cap.release()
cv2.destroyAllWindows()

# import cv2
# import os
# import numpy as np
# import pickle
# import cvzone
# import face_recognition
# import datetime
# import firebase_admin
# from firebase_admin import credentials
# from firebase_admin import db
# from firebase_admin import storage

# cred = credentials.Certificate("serviceAccountKey.json")
# firebase_admin.initialize_app(cred, {
#     'databaseURL' : 'https://facialattendance-d2c63-default-rtdb.firebaseio.com/',
#     'storageBucket' : 'facialattendance-d2c63.appspot.com'
#     })

# bucket = storage.bucket()
# # open default camera (index 0)
# cap = cv2.VideoCapture(0)
# cap.set(3, 640)
# cap.set(4, 480)
# imgBackground = cv2.imread('Resources/background.png')

# # Importing images to list
# folderModePath = 'Resources/Modes'
# modePath = os.listdir(folderModePath)
# imgModeList = []
# for path in modePath:
#     imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))
# #import the encoding file
# file = open('EncodeFile.p', 'rb')
# encodeKnownwithIds = pickle.load(file)
# file.close()
# encodeKnown, studId = encodeKnownwithIds
# #print(studId)

# modeType = 0
# counter = 0
# id=-1
# while True:
#     # read a frame from the camera
#     ret, frame = cap.read()
#     imgS = cv2.resize(frame, (0,0), None, 0.25, 0.25)
#     imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

#     faceCurFrame = face_recognition.face_locations(imgS)
#     encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

#     imgBackground[162:162+480, 55:55+640] = frame
#     imgBackground[44:44+633, 808:808+414] = imgModeList[modeType]

#     if faceCurFrame:
#         for i, encodeFace in enumerate(encodeCurFrame):
#             matches = face_recognition.compare_faces(encodeKnown, encodeFace)
#             faceDis = face_recognition.face_distance(encodeKnown, encodeFace)

#             print("matches", matches)
#             print("faceDis", faceDis)

#             matchIndex = np.argmin(faceDis)

#             if matches[matchIndex]:
#                 print("Face Detected")
#                 print(studId[matchIndex])
#                 y1, x2, y2, x1 = faceCurFrame[i]
#                 y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
#                 bbox = 55+x1, 162+y1, x2-x1, y2-y1 
#                 cvzone.cornerRect(imgBackground, bbox)
#                 id = studId[matchIndex]
#                 if counter==0:
#                     cvzone.putTextRect(imgBackground, "Loading", (275, 400))
#                     cv2.imshow("Face Attendance", imgBackground)
#                     cv2.waitKey(1)
#                     counter=1
#                     modeType=1
#         if counter!=0:
#             for id in set([studId[i] for i, m in enumerate(matches) if m]):
#                 if counter == 1:
#                     studentInfo = db.reference(f'Students/{id}').get()
#                     print(studentInfo)
#                      # Get the Image from the storage
#                     blob = bucket.get_blob(f'Images/{id}.jpg')
#                     array = np.frombuffer(blob.download_as_string(), np.uint8)
#                     imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)
#                      # Update data of attendance
#                     datetimeObject = datetime.datetime.strptime(studentInfo['last_attendance'],
#                                                        "%Y-%m-%d %H:%M:%S")
#                     secondsElapsed = (datetime.datetime.now() - datetimeObject).total_seconds()
#                     print(secondsElapsed)
#                     if secondsElapsed > 30:
#                         ref = db.reference(f'Students/{id}')
#                         studentInfo['total_attendance'] += 1
#                         ref.child('total_attendance').set(studentInfo['total_attendance'])
#                         ref.child('last_attendance').set(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
#                     else:
#                         modeType = 3
#                         counter = 0
#                         imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
#                 if modeType != 3:
         
#                     if 10 < counter < 20:
#                         modeType = 2
#                         imgBackground[44:44 + 633, 808:808+414] = imgModeList[modeType]
#                         # imgBackground[44:44 + 633, 808:808+414] = imgModeList[modeType]
#                         counter += 1
#                         cvzone.putTextRect(imgBackground, f"Attendance recorded for ID {id}", (200, 400), fontScale=1.5)
#                         cv2.imshow("Face Attendance", imgBackground)
#                         cv2.waitKey(1500)
#                         modeType = 3
#                         counter = 0
#                         imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
#     # cv2.putText(imgBackground, f"Attendance Confirmed for {id}", (55, 120), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,0,255), 2)

#     # cvzone.putTextRect(imgBackground, f"Attendance Confirmed for {id}", (55, 120), fontScale=2, thickness=3)
#     cv2.imshow("Face Attendance", imgBackground)
#     # cv2.waitKey(3000)
#     # modeType = 3
#     # counter = 0
#     # imgBackground[44:44+633, 808:808+414] = imgModeList[modeType]
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# # release the camera and close the window
# cap.release()
# cv2.destroyAllWindows()



