# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect
from flask_bootstrap import Bootstrap
import sqlite3
import cv2,os
import shutil
import numpy as np
from PIL import Image, ImageTk
import pandas as pd
import datetime
import time
# import mysql.connector
# import RPi.GPIO as GPIO
# from mfrc522 import SimpleMFRC522
import glob
# from Adafruit_CharLCD import Adafruit_CharLCD



app = Flask(__name__)
Bootstrap(app)


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False
Attendance=0


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/start')
def start():
    return render_template('start.html')


@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/submit', methods=['POST'])
def submit():
    roll_no = request.form.get('roll_no')
    name = request.form.get('name')
    class_ = request.form.get('class')
    division = request.form.get('division')

    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    # c.execute('''
    #     CREATE TABLE IF NOT EXISTS students
    #     (roll_no INTEGER PRIMARY KEY AUTOINCREMENT,
    #     name TEXT,
    #     class TEXT,
    #     division TEXT,
    #     Attendance INTEGER)
    #     ''')


    if(is_number(roll_no)):
        cam = cv2.VideoCapture(0)
        harcascadePath = "haarcascade_frontalface_default.xml"
        detector=cv2.CascadeClassifier(harcascadePath)
        sampleNum=0
        while(True):
            ret, img = cam.read()
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = detector.detectMultiScale(gray, 1.3, 5)
            for (x,y,w,h) in faces:
                cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
                #incrementing sample number
                sampleNum=sampleNum+1
                #saving the captured face in the dataset folder TrainingImage
                cv2.imwrite("T:/bepro/TrainingImage/ "+name +"."+roll_no +'.'+ str(sampleNum) + ".jpg", gray[y:y+h,x:x+w])
                #display the frame
                cv2.imshow('frame',img)
            #wait for 100 miliseconds
            if cv2.waitKey(100) & 0xFF == ord('q'):
                break
            # break if the sample number is morethan 100
            elif sampleNum>100:
                break
        cam.release()
        cv2.destroyAllWindows()
        res = "Images Saved for roll_no : " + roll_no +" Name : "+ name
        row = [roll_no , name]
        #sending the registered student data to the database
        c.execute('''
                INSERT INTO students (roll_no, name, class, division,Attendance)
                VALUES (?, ?, ?, ?, ?)
                ''', (roll_no, name, class_, division, Attendance))

        conn.commit()
        print("Records inserted........")
        # message.configure(text= res)
    else:
        if(is_number(roll_no)):
            res = "Enter Alphabetical Name"
            # message.configure(text= res)
        if(name.isalpha()):
            res = "Enter Numeric roll_no"
            # message.configure(text= res)


    conn.close()

    return redirect('/start')

def getImagesAndLabels(path):
    #get the path of all the files in the folder
    imagePaths=[os.path.join(path,f) for f in os.listdir(path)]
    #print(imagePaths)

    #create empth face list
    faces=[]
    #create empty roll_no list
    roll_nos=[]
    #now looping through all the image paths and loading the roll_nos and the images
    for imagePath in imagePaths:
        #loading the image and converting it to gray scale
        pilImage=Image.open(imagePath).convert('L')
        #Now we are converting the PIL image into numpy array
        imageNp=np.array(pilImage,'uint8')
        #getting the roll_no from the image
        roll_no=int(os.path.split(imagePath)[-1].split(".")[1])
        # extract the face from the training image sample
        faces.append(imageNp)
        roll_nos.append(roll_no)
    return faces,roll_nos


@app.route('/TrainImages')
def TrainImages():
    recognizer = cv2.face_LBPHFaceRecognizer.create()#recognizer = cv2.face.LBPHFaceRecognizer_create()#$cv2.createLBPHFaceRecognizer()
    harcascadePath = "haarcascade_frontalface_default.xml"
    detector =cv2.CascadeClassifier(harcascadePath)
    faces,roll_no = getImagesAndLabels("TrainingImage")
    recognizer.train(faces, np.array(roll_no))
    recognizer.save("T:/bepro/TrainingImageLabel/Trainner.yml")
    res = "Image Trained"#+",".join(str(f) for f in roll_no)
    # message.configure(text= res)
    print("op")
    return redirect('/start')


# # instantiate lcd and specify pins
# lcd = Adafruit_CharLCD(rs=21, en=24, d4=23, d5=17, d6=18, d7=22, cols=16, lines=2)
# lcd.clear()

@app.route('/TrackImages')
def TrackImages():

    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    # lcd.message("Scan your RFID")

    # reader = SimpleMFRC522()
    # roll_no, text = reader.read()
    # rfid = int(text)
    # lcd.clear()
    # text = "roll_no {} Recognized".format(rfid)
    # lcd.message(text)
    rfid = int(input())

    recognizer = cv2.face.LBPHFaceRecognizer_create()  # cv2.createLBPHFaceRecognizer()
    recognizer.read(
        "T:/bepro/TrainingImageLabel/Trainner.yml")
    harcascadePath = "T:/bepro/haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(harcascadePath);
    roll_no = "Unknown"
    tt = str(roll_no)
    z = 0
    if (rfid > 0):
        cam = cv2.VideoCapture(0)
        font = cv2.FONT_HERSHEY_SIMPLEX
        col_names = ['roll_no', 'Name', 'Attendance']
        students = pd.DataFrame(columns=col_names)
        time.sleep(2)
        # lcd.clear()
        # lcd.message("Identifying")
        while True:
            # Detection
            ret, im = cam.read()
            gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
            faces = faceCascade.detectMultiScale(gray, 1.3, 5)
            # Recognition
            for (x, y, w, h) in faces:
                cv2.rectangle(im, (x, y), (x + w, y + h), (225, 0, 0), 2)
                roll_no, conf = recognizer.predict(gray[y:y + h, x:x + w])
                if (conf < 50):
                    ts = time.time()
                    aa = c.execute("SELECT [name] FROM students WHERE roll_no = {}".format(roll_no))
                    aa = c.fetchone()
                    tt = str(roll_no) + "-" + aa[0]

                else:
                    roll_no = 'Unknown'
                    tt = str(roll_no)

                if (conf >75):
                    noOfFile = len(os.listdir(
                        "T:/bepro/ImagesUnknown")) + 1
                    cv2.imwrite(
                        "T:/bepro/ImagesUnknown/Image" + str(
                            noOfFile) + ".jpg", im[y:y + h, x:x + w])

                cv2.putText(im, str(tt), (x, y + h), font, 1, (255, 255, 255), 2)
                students = students.drop_duplicates(subset=['roll_no'], keep='last')

            cv2.imshow('Recognizer', im)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cam.release()
        cv2.destroyAllWindows()

        # Database
        if (rfid == roll_no):
            c.execute("""UPDATE students set Attendance=Attendance+1 where roll_no={}""".format(roll_no))
            conn.commit()
            Attendance = c.execute("SELECT [Attendance] FROM students WHERE roll_no = {}".format(roll_no))
            Attendance = c.fetchone()
            students.loc[len(students)] = [roll_no, aa[0], Attendance[0]]
            res = students
            text = " Attendance Updated\n -{}".format(aa[0])

        #     # message2.configure(text=res)
        #
        #     # lcd.clear()
        #     # lcd.message(text)
        #     for x in range(0, 3):
        #         lcd.move_left()
        #         time.sleep(2)
        #     time.sleep(1)
        #
        #     for x in range(0, 2):
        #         lcd.move_right()
        #         time.sleep(1)
        #     time.sleep(2)
        #     lcd.clear()
        #
        # else:
        #     lcd.clear()
        #     res = "roll_no Mismatch"
        #     lcd.message(res)
        #     message2.configure(text=res)
        #     # print(students)
        #     time.sleep(3)
        # lcd.clear()

    return redirect('/start')

@app.route('/close')
def close():
    return render_template('close.html')


if __name__ == '__main__':
    app.run(debug=True)