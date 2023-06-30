import face_recognition
import cv2
import os
import re
import sys
from PyQt5.QtWidgets import QWidget, QApplication, QDialog
from PyQt5.QtGui import QPainter
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt, pyqtSlot
import numpy as np

# first = True

DATA_PATH = 'data'

class InputWidget(QDialog):
    def __init__(self, name, frame, *args, **kwargs):
        super(InputWidget, self).__init__(*args, **kwargs)
        loadUi("widget.ui", self)
        self.frame = cur_frame
        self.name = name
        if name is not 'Unknown':
            self.lineEdit.setText(name)


        self.btn_OK.clicked.connect(self.onOK)
        self.btn_Cancel.clicked.connect(self.onCancel)



    @pyqtSlot()
    def onOK(self):
        if self.name is not 'Unknown':
            remove_face_data(self.name)
        add_face_data(self.lineEdit.text(), self.frame)
        self.close()


    @pyqtSlot()
    def onCancel(self):
        self.close()

def image_files_in_folder(folder):
    return [os.path.join(folder, f) for f in os.listdir(folder) if re.match(r'.*\.(jpg|jpeg|png)', f, flags=re.I)]

def get_face_data():
    for file in image_files_in_folder(DATA_PATH):
        basename = os.path.splitext(os.path.basename(file))[0]
        img = face_recognition.load_image_file(file)
        encodings = face_recognition.face_encodings(img)

        if len(encodings) > 1:
            print("WARNING: More than one face found in {}. Only considering the first face.".format(file))

        if len(encodings) == 0:
            print("WARNING: No faces found in {}. Ignoring file.".format(file))
        else:
            known_face_names.append(basename)
            known_face_encodings.append(encodings[0])

def add_face_data(name, frame):
    img_path = DATA_PATH + '/' + name + '.jpg'
    cv2.imwrite(img_path, frame)
    
    img = face_recognition.load_image_file(img_path)
    encodings = face_recognition.face_encodings(img)

    if len(encodings) > 1:
        print("WARNING: More than one face found in {}. Only considering the first face.".format(file))

    if len(encodings) == 0:
        print("WARNING: No faces found in {}. Ignoring file.".format(file))
    else:
        known_face_names.append(name)
        known_face_encodings.append(encodings[0])

def remove_face_data(name):
    if os.path.exists(DATA_PATH + '/' + name + '.jpg'):
            os.remove(DATA_PATH + '/' + name + '.jpg')

    index = known_face_names.index(name)
    if index >= 0:
        known_face_names.pop(index)
        known_face_encodings.pop(index)


def set_face_name(event, x, y, flags, first):
    # First click initialize the init rectangle point
    flag, name = is_cursor_inside_face_regions(x, y)
    if event == cv2.EVENT_LBUTTONDOWN and flag:
        if first == True:
            app = QApplication(sys.argv)
            first = False
        widget = InputWidget(name, cur_frame)
        widget.show()
        app.exec()

def is_cursor_inside_face_regions(x, y):
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4
        if left <= x and x <= right and top <= y and y <= bottom:
            return True, name
    return False, ''

def main():
    global known_face_names
    global known_face_encodings
    global face_locations
    global face_encodings
    global face_names
    global first

    first = True

    known_face_names = []
    known_face_encodings = []

    face_locations = []
    face_encodings = []
    face_names = []
    # Get a reference to webcam #0 (the default one)
    video_capture = cv2.VideoCapture(0)

    matchCnt = 0
    detectFaces = 0
    cv2.namedWindow('Video')
    get_face_data()
    cv2.setMouseCallback('Video', set_face_name, first)

# for file in image_files_in_folder('data'):
#     basename = os.path.splitext(os.path.basename(file))[0]
#     img = face_recognition.load_image_file(file)
#     encodings = face_recognition.face_encodings(img)

#     if len(encodings) > 1:
#         print("WARNING: More than one face found in {}. Only considering the first face.".format(file))

#     if len(encodings) == 0:
#         print("WARNING: No faces found in {}. Ignoring file.".format(file))
#     else:
#         known_face_names.append(basename)
#         known_face_encodings.append(encodings[0])

    # Initialize some variables
    process_this_frame = True
    global cur_frame
    while True:
        # Grab a single frame of video
        ret, frame = video_capture.read()
        cur_frame = np.copy(frame)
        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]

        # Only process every other frame of video to save time
        if process_this_frame:
            # Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            if len(face_locations) > 0:
                detectFaces += 1
            face_names = []
            for face_encoding in face_encodings:
                # See if the face is a match for the known face(s)
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"

                # If a match was found in known_face_encodings, just use the first one.
                if True in matches:
                    matchCnt += 1
                    first_match_index = matches.index(True)
                    name = known_face_names[first_match_index]

                face_names.append(name)

        process_this_frame = not process_this_frame


        # Display the results
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        # Display the resulting image
        cv2.imshow('Video', frame)

        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.imwrite('result.jpg', frame)
            break

    print(matchCnt, ' ======== ', detectFaces)
    print(matchCnt / detectFaces * 100) 
    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)
    main()
    
