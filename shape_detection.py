import cv2

from picamera2 import Picamera2
import numpy as np

picam2 = Picamera2()
picam2.start()

while True:
    image = picam2.capture_array()
    h,w = image.shape[:2]
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    _, thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV) #threshold for black and white

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


    for cnt in contours:
        area = cv2.contourArea(cnt)
        
        if area < 500:
            continue
        perimeter = cv2.arcLength(cnt, True)
        
        if perimeter == 0:
            continue

        # Polygon approximation
        eps = 0.03 * perimeter
        approx = cv2.approxPolyDP(cnt, eps, True)
        vertex = len(approx)
        

        
        # Circularity 
        c = 4 * np.pi * float(area) / (perimeter**2)

        # Aspect Ratio (width/height)
        x,y,w,h = cv2.boundingRect(approx)
        ar = w / h
        
        shape = "Unknown"
        if 9 <= vertex <=11:
            shape = "Star"
        elif 7 <= vertex <= 9:
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
