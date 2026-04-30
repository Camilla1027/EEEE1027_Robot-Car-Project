import RPi.GPIO as GPIO
import time
import cv2
import numpy as np
from picamera2 import Picamera2


# symbol thresholds 
symbol_thresholds = {
    'arrow_up': 0.4,
    'arrow_down': 0.6,
    'arrow_left': 0.5,
    'arrow_right': 0.6,
    'QR': 0.38,
    'fingerprint': 0.3,
    'warning': 0.6,
    'hand': 0.6,
    'recycle': 0.4
}

templates = {
    'arrow_right': cv2.imread('/home/pi/Downloads/arrow_right.jpeg', 0),
    'arrow_down': cv2.imread('/home/pi/Downloads/arrow_down.jpeg', 0),
    'arrow_left': cv2.imread('/home/pi/Downloads/arrow_left.jpeg', 0),
    'arrow_up': cv2.imread('/home/pi/Downloads/arrow_up.jpeg', 0),
    'QR': cv2.imread('/home/pi/Downloads/qr.jpeg',0),
    'fingerprint': cv2.imread('/home/pi/Downloads/fingerprint.jpeg',0),
    'recycle': cv2.imread('/home/pi/Downloads/recycle.jpeg',0),
    'warning': cv2.imread('/home/pi/Downloads/warning.jpeg',0),
    'hand': cv2.imread('/home/pi/Downloads/hand.jpeg',0),

    
}
sizes = {
    'arrow_right': (220, 100),
    'arrow_left': (220, 100),
    'arrow_up': (220, 100),
    'arrow_down': (220, 100),
    'QR': (220, 100),
    'fingerprint': (220, 100),
    'recycle': (220, 100),
    'warning': (200, 100),
    'hand': (200, 100)
}

for name in templates:
    if templates[name] is not None:
        templates[name] = cv2.resize(templates[name], sizes[name])

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(
    main={"format": "RGB888", "size": (640, 480)}
))
picam2.start()

GPIO.setmode(GPIO.BCM)

IN1, IN2, IN3, IN4 = 21, 20, 16, 12
ENA, ENB = 24, 23
motor = 17

GPIO.setup([IN1, IN2, IN3, IN4, ENA, ENB, motor], GPIO.OUT)

pwm = GPIO.PWM(motor, 20)
pwm.start(50)

pwmA = GPIO.PWM(ENA, 1000)
pwmB = GPIO.PWM(ENB, 1000)
pwmA.start(50)
pwmB.start(50)

def forward():
    GPIO.output(IN1, 0)
    GPIO.output(IN2, 1)
    GPIO.output(IN3, 0)
    GPIO.output(IN4, 1)
    pwmA.ChangeDutyCycle(30)
    pwmB.ChangeDutyCycle(30)

def stop():
    GPIO.output(IN1, 0)
    GPIO.output(IN2, 0)
    GPIO.output(IN3, 0)
    GPIO.output(IN4, 0)

def left():
    GPIO.output(IN1, 0)
    GPIO.output(IN2, 1)
    GPIO.output(IN3, 1)
    GPIO.output(IN4, 0)
    pwmA.ChangeDutyCycle(70)
    pwmB.ChangeDutyCycle(10)

def right():
    GPIO.output(IN1, 1)
    GPIO.output(IN2, 0)
    GPIO.output(IN3, 0)
    GPIO.output(IN4, 1)
    pwmA.ChangeDutyCycle(10)
    pwmB.ChangeDutyCycle(70)
    
def spin():
    GPIO.output(IN1, 1)
    GPIO.output(IN2, 0)
    GPIO.output(IN3, 0)
    GPIO.output(IN4, 1)

    pwmA.ChangeDutyCycle(70)
    pwmB.ChangeDutyCycle(70)
    
def detect_line(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    black_mask = cv2.inRange(hsv, (0, 0, 0), (180, 255, 50))
    yellow_mask = cv2.inRange(hsv, (20, 100, 100), (35, 255, 255))

    red_mask1 = cv2.inRange(hsv, (0, 100, 100), (10, 255, 255))
    red_mask2 = cv2.inRange(hsv, (160, 100, 100), (180, 255, 255))
    red_mask = red_mask1 + red_mask2

    if np.sum(yellow_mask) > 5000:
        return yellow_mask
    elif np.sum(red_mask) > 5000:
        return red_mask
    else:
        return black_mask

def detection(frame):
    symbol = None
    
    for symbol_name, template in templates.items():

        if template is None:
            continue
        
        h, w = template.shape
        result = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        print(symbol_name, "Score: ", max_val )
        if max_val >= symbol_thresholds.get(symbol_name, 0.5):
            symbol = symbol_name
            return symbol

frame_count = 0
N = 10

try:
    while True:
        frame = picam2.capture_array()
        frame = cv2.resize(frame, [320,240])
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cv2.imshow("Camera", frame)
        cv2.waitKey(1)
        h, w = gray.shape
        

        mask = detect_line(frame)

        roi_line = mask[int(h*0.6):h, :]
        M = cv2.moments(roi_line)

        if M["m00"] > 0:
            cx = int(M["m10"] / M["m00"])

            if cx < w/3:
                left()
            elif cx > 2*w/3:
                right()
            else:
                forward()

        time.sleep(0.02)
        
        frame_count += 1
        
        if frame_count % N == 0:
            roi = gray[int(h*0.2):int(h*0.6), int(w*0.2):int(w*0.8)]

            symbol = detection(roi)

            
            if symbol is not None:
                print(symbol)
            
                if symbol == "arrow_left":
                    left()
                    time.sleep(1)
                elif symbol == "arrow_right":
                    right()
                    time.sleep(1)
                elif symbol == "warning" or symbol == "hand":
                    stop()
                    time.sleep(1)
                elif symbol == "recycle":
                    spin()
                    time.sleep(2.1) 
    

finally:
    GPIO.cleanup()
    picam2.stop()
