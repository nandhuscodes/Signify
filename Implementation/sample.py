import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import math
import time
import os

# Define the path to the image
image_path = 'img.jpg'

# Check if the image path exists
if not os.path.exists(image_path):
    print("Image not found.")
    exit()

# Initialize HandDetector
detector = HandDetector(maxHands=1)
offset = 20
imgSize = 300
counter = 0

folder = 'Data/Stop'

# Read the image
img = cv2.imread(image_path)

hands, img = detector.findHands(img)
if hands:
    hand = hands[0]
    x, y, w, h= hand['bbox']
    
    imgWhite = np.ones((imgSize, imgSize, 3), np.uint8)*255
    imgCrop = img[y-offset: y+h+offset, x-offset: x+w+offset]
    imgCropSize = imgCrop.shape

    aspectRatio = h/w

    if aspectRatio > 1:
        k = imgSize/h
        wCal = math.ceil(k*w)
        imgResize = cv2.resize(imgCrop, (wCal, imgSize))
        imgResizeShape = imgResize.shape
        wGap = math.ceil((imgSize-wCal)/2)
        imgWhite[:, wGap: wCal + wGap] = imgResize
    else:
        k = imgSize/w
        hCal = math.ceil(k*h)
        imgResize = cv2.resize(imgCrop, (imgSize, hCal))
        imgResizeShape = imgResize.shape
        hGap = math.ceil((imgSize-hCal)/2)
        imgWhite[hGap: hCal + hGap, :] = imgResize
    cv2.imshow('ImageCrop', imgCrop)
    cv2.imshow('ImageWhite', imgWhite)

cv2.imshow('Image', img)
key = cv2.waitKey(0)
if key == ord("s"):
    counter += 1
    cv2.imwrite(f'{folder}/wanna_{time.time()}.jpg', imgWhite)
    print(counter)
elif key == ord('q'):
    cv2.destroyAllWindows()  # Destroy all OpenCV windows
