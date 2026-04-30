import cv2
from picamera2 import Picamera2
import numpy as np

picam2 = Picamera2()
picam2.start()

threshold = 0.6
  
templates = {
    'arrow_up': cv2.imread('/home/pi/Downloads/arrow_up.jpeg', 0),
    'arrow_down': cv2.imread('/home/pi/Downloads/arrow_down.jpeg', 0),
    'arrow_left': cv2.imread('/home/pi/Downloads/arrow_left.jpeg', 0),
    'arrow_right': cv2.imread('/home/pi/Downloads/arrow_right.jpeg', 0),
    'qr': cv2.imread('/home/pi/Downloads/qr.jpeg', 0),
    'recycle': cv2.imread('/home/pi/Downloads/recycle.jpeg', 0),
    'warning': cv2.imread('/home/pi/Downloads/warning.jpeg', 0),
    'fingerprint': cv2.imread('/home/pi/Downloads/fingerprint.jpeg', 0),
    'hand': cv2.imread('/home/pi/Downloads/hand.jpeg', 0)
}


while True:
    image = picam2.capture_array()
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
    for symbol_name, template in templates.items():
        
        if template is None:
            continue
        
        h, w = template.shape

        result = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        
        print(symbol_name, "score:", max_val)

        if max_val >= threshold:
            top_left = max_loc
            bottom_right = (top_left[0] + w, top_left[1] + h)

            cv2.rectangle(image, top_left, bottom_right, (0,255,0), 2)

            cv2.putText(image, symbol_name, (top_left[0], top_left[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

    cv2.imshow("Camera", image)

    if cv2.waitKey(1) == 27: 
        break