from flask import Flask, render_template, Response, jsonify
import cv2
import numpy as np
from cvzone.HandTrackingModule import HandDetector
import math
from tensorflow.keras.models import load_model

app = Flask(__name__)

class HandRecognition:
    def __init__(self):
        self.detector = HandDetector(maxHands=1)
        self.model = load_model('Model/uyir_model.h5')
        self.cap = cv2.VideoCapture(0)
        self.offset = 20
        self.imgSize = 300
        self.labels = ['அ', 'ஆ', 'இ', 'ஈ', 'உ', 'ஊ', 'எ', 'ஏ', 'ஐ', 'ஒ', 'ஓ', 'ஔ', 'ஃ']

    def get_frame(self):
        while True:
            success, img = self.cap.read()
            imgOutput = img.copy()
            hands, img = self.detector.findHands(img)
            if hands:
                hand = hands[0]
                x, y, w, h = hand['bbox']

                imgCrop = img[y - self.offset:y + h + self.offset, x - self.offset:x + w + self.offset]
                letter = self.predict_letter_from_bbox(imgCrop)

                #cv2.rectangle(imgOutput, (x, y), (x + w, y + h), (255, 0, 0), 2)
                #cv2.putText(imgOutput, letter, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            ret, buffer = cv2.imencode('.jpg', cv2.cvtColor(imgOutput, cv2.COLOR_BGR2BGRA))
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    def predict_letter_from_bbox(self, imgCrop):
        imgCrop = self.preprocess_image(imgCrop)
        prediction = self.model.predict(imgCrop)
        predicted_class = np.argmax(prediction)
        predicted_letter = self.labels[predicted_class]
        return predicted_letter

    def preprocess_image(self, img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert image to RGB
        img = cv2.resize(img, (self.imgSize, self.imgSize))   # Resize to model's input shape
        img = np.expand_dims(img, axis=0)           # Add batch dimension
        img = img / 255.0                           # Normalize pixel values
        return img

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(hand_recognition.get_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/sign_class')
def sign_class():
    # Capture an image to pass to the prediction method
    success, img = hand_recognition.cap.read()
    hands, _ = hand_recognition.detector.findHands(img)
    if hands:
        hand = hands[0]
        x, y, w, h = hand['bbox']
        imgCrop = img[y - hand_recognition.offset:y + h + hand_recognition.offset, x - hand_recognition.offset:x + w + hand_recognition.offset]
        detected_sign_class = hand_recognition.predict_letter_from_bbox(imgCrop)
        return jsonify({"sign_class": detected_sign_class})
    else:
        return jsonify({"sign_class": ""})  # Return empty string if no hands detected

if __name__ == "__main__":
    hand_recognition = HandRecognition()
    app.run(debug=True)
