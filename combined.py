import RPi.GPIO as GPIO
import time
import cv2
from picamera2 import Picamera2
import numpy as np

picam2 = Picamera2()
picam2.start()


symbol_thresholds = {
    'arrow_up': 0.6,
    'arrow_down': 0.7,
    'arrow_left': 0.6,
    'arrow_right': 0.6,
    'qr': 0.6,
    'recycle': 0.6,
    'warning': 0.35,       
    'fingerprint': 0.6,
    'hand': 0.36,
    'Star': 0.7
}

templates = {
    'arrow_up': cv2.imread('/home/pi/Downloads/arrow_up.jpeg', 0),
    'arrow_down': cv2.imread('/home/pi/Downloads/arrow_down.jpeg', 0),
    'arrow_left': cv2.imread('/home/pi/Downloads/arrow_left.jpeg', 0),
    'arrow_right': cv2.imread('/home/pi/Downloads/arrow_right.jpeg', 0),
    'qr': cv2.imread('/home/pi/Downloads/qr.jpeg', 0),
    'recycle': cv2.imread('/home/pi/Downloads/recycle.jpeg', 0),
    'warning': cv2.imread('/home/pi/Downloads/warning.jpeg', 0),
    'fingerprint': cv2.imread('/home/pi/Downloads/fingerprint.jpeg', 0),
    'hand': cv2.imread('/home/pi/Downloads/hand.jpeg', 0),
    'Star': cv2.imread('/home/pi/Downloads/Star.jpeg', 0)

}

while True:
    image = picam2.capture_array()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    matched = False

    # Template Matching
    for symbol_name, template in templates.items():
        if template is None:
            continue

        h, w = template.shape
        result = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        
        if max_val >= symbol_thresholds.get(symbol_name, 0.6):
            top_left = max_loc 
            bottom_right = (top_left[0] + w, top_left[1] + h)
            cv2.rectangle(image, top_left, bottom_right, (0,255,0), 2)
            cv2.putText(image, symbol_name, (top_left[0], top_left[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
            matched = True
            break 

    # Contour Detection
    if not matched:
        _, thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < 500:
                continue
            perimeter = cv2.arcLength(cnt, True)
            if perimeter == 0:
                continue

            approx = cv2.approxPolyDP(cnt, 0.03 * perimeter, True)
            vertex = len(approx)

            x, y, w, h = cv2.boundingRect(approx)
            ar = w / h
            c = 4 * np.pi * area / (perimeter ** 2)

            shape = "Unknown"
            if 7 <= vertex <= 9:
                if 0.1 < c < 0.6:
                    shape = "Three-quarter circle"
                else:
                    shape = "Octagon"
            elif 11 <= vertex <= 13:
                shape = "Cross"
            elif 3 <= vertex <= 5:
                if 0.9 < ar < 1.1:
                    shape = "Trapezium"
                else:
                    shape = "Rhombus"
            elif 0.5 < c < 0.8:
                shape = "Semicircle"

            cv2.drawContours(image, [cnt], -1, (0,255,0), 2)
            cv2.putText(image, shape, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

    cv2.imshow("Camera", image)
    if cv2.waitKey(1) == 27: 
        break

cv2.destroyAllWindows()