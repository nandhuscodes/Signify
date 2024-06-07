from flask import Flask, render_template, Response, jsonify
import cv2
import numpy as np
from cvzone.HandTrackingModule import HandDetector
from cvzone.ClassificationModule import Classifier
import math

language = "english"

app = Flask(__name__)

class HandRecognition:
    def __init__(self):
        global language
        self.detector = HandDetector(maxHands=1)
        self.classifier = Classifier("word_model.h5", "labels.txt")
        self.cap = cv2.VideoCapture(0)
        self.offset = 20
        self.imgSize = 300
        self.update_classifier()

    def update_classifier(self):
        global language
        if language == "tamil":
            self.classifier = Classifier("Model/uyirmei_t_model.h5", "Model/um_t_labels.txt")
            self.labels = ['அ', 'ஆ', 'இ', 'ஈ', 'உ', 'ஊ', 'எ', 'ஏ', 'ஐ', 'ஒ', 'ஓ', 'ஔ', 'ஃ', 'க்', 'ங்','ச்','ஞ்','ட்','ண்','த்','ந்','ப்','ம்','ய்','ர்','ல்','வ்','ழ்','ள்','ற்','ன்']
        else:
            self.classifier = Classifier("word_model.h5", "labels.txt")
            self.labels = ['Bathroom', 'Break', 'Call', 'Cute', 'Dad', 'Dislike', 'Drink', 'Fighting', 'Food', 'Happy', 'Hello', 'I Love You', 'Its Me', 'Like', 'Milk', 'Mom', 'Name', 'No', 'Ok', 'Peace', 'Promise', 'Ready', 'Saying', 'Sibling', 'Silence', 'Stop', 'Terrific', 'Thank You', 'Water', 'Yes']
    
    def toggle_language(self):
        global language
        language = "tamil" if language == "english" else "english"
        self.update_classifier()

    def get_frame(self):
        while True:
            success, img = self.cap.read()
            imgOutput = img.copy()
            hands, img = self.detector.findHands(img)
            if hands:
                hand = hands[0]
                x, y, w, h = hand['bbox']

                imgWhite = np.ones((self.imgSize, self.imgSize, 3), np.uint8) * 255
                imgCrop = img[y - self.offset:y + h + self.offset, x - self.offset:x + w + self.offset]

                imgCropShape = imgCrop.shape

                aspectRatio = h / w

                if aspectRatio > 1:
                    k = self.imgSize / h
                    wCal = math.ceil(k * w)
                    imgResize = cv2.resize(imgCrop, (wCal, self.imgSize))
                    imgResizeShape = imgResize.shape
                    wGap = math.ceil((self.imgSize - wCal) / 2)
                    imgWhite[:, wGap:wCal + wGap] = imgResize
                    prediction, index = self.classifier.getPrediction(imgWhite, draw=False)
                    predicted_word = self.labels[index]

                else:
                    k = self.imgSize / w
                    hCal = math.ceil(k * h)
                    imgResize = cv2.resize(imgCrop, (self.imgSize, hCal))
                    imgResizeShape = imgResize.shape
                    hGap = math.ceil((self.imgSize - hCal) / 2)
                    imgWhite[hGap:hCal + hGap, :] = imgResize
                    prediction, index = self.classifier.getPrediction(imgWhite, draw=False)
                    predicted_word = self.labels[index]

                ret, buffer = cv2.imencode('.jpg', cv2.cvtColor(imgOutput, cv2.COLOR_BGR2BGRA))
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

            else:
                ret, buffer = cv2.imencode('.jpg', cv2.cvtColor(imgOutput, cv2.COLOR_BGR2BGRA))
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    def detect_sign_class(self):
        while True:
            success, img = self.cap.read()
            imgOutput = img.copy()
            hands, img = self.detector.findHands(img)
            if hands:
                hand = hands[0]
                x, y, w, h = hand['bbox']

                imgWhite = np.ones((self.imgSize, self.imgSize, 3), np.uint8) * 255
                imgCrop = img[y - self.offset:y + h + self.offset, x - self.offset:x + w + self.offset]

                imgCropShape = imgCrop.shape

                aspectRatio = h / w

                if aspectRatio > 1:
                    k = self.imgSize / h
                    wCal = math.ceil(k * w)
                    imgResize = cv2.resize(imgCrop, (wCal, self.imgSize))
                    imgResizeShape = imgResize.shape
                    wGap = math.ceil((self.imgSize - wCal) / 2)
                    imgWhite[:, wGap:wCal + wGap] = imgResize
                    prediction, index = self.classifier.getPrediction(imgWhite, draw=False)
                    predicted_word = self.labels[index]

                else:
                    k = self.imgSize / w
                    hCal = math.ceil(k * h)
                    imgResize = cv2.resize(imgCrop, (self.imgSize, hCal))
                    imgResizeShape = imgResize.shape
                    hGap = math.ceil((self.imgSize - hCal) / 2)
                    imgWhite[hGap:hCal + hGap, :] = imgResize
                    prediction, index = self.classifier.getPrediction(imgWhite, draw=False)
                    predicted_word = self.labels[index]

                return predicted_word

    def release_camera(self):
        self.cap.release()

@app.route('/')
def index():
    return render_template('index1.html')

@app.route('/video_feed')
def video_feed():
    return Response(hand_recognition.get_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/sign_class')
def sign_class():
    detected_sign_class = hand_recognition.detect_sign_class()
    return jsonify({"sign_class": detected_sign_class})

@app.route('/toggle_language', methods=['POST'])
def toggle_language():
    hand_recognition.toggle_language()
    return jsonify({"message": language})

if __name__ == "__main__":
    hand_recognition = HandRecognition()
    app.run(debug=True)
