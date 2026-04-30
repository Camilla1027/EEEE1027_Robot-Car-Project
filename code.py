import RPi.GPIO as GPIO
import time
import cv2

from picamera2 import Picamera2
import numpy as np


# symbol thresholds 
symbol_thresholds = {
    'arrow_up': 0.6,
    'arrow_down': 0.7,
    'arrow_left': 0.6,
    'arrow_right': 0.6,
    'qr': 0.34,
    'recycle': 0.34,
    'fingerprint': 0.6,
    'hand': 0.5,
    'warning': 0.4
    }

templates = {
    'arrow_up': cv2.imread('/home/pi/Desktop/arrow_up.jpg', 0),
    'arrow_down': cv2.imread('/home/pi/Desktop/arrow_down.jpg', 0),
    'arrow_left': cv2.imread('/home/pi/Desktop', 0),
    'arrow_right': cv2.imread('/home/pi/Desktop', 0),
    'qr': cv2.imread('/home/pi/Desktop/qr.jpg', 0),
    'recycle': cv2.imread('/home/pi/Desktop/recycle.jpg', 0),
    'warning': cv2.imread('/home/pi/Desktop/warning.jpg', 0),
    'fingerprint': cv2.imread('/home/pi/Desktop/fingerprint.jpg', 0),
    'hand': cv2.imread('/home/pi/Desktop/hand.jpg', 0)
}

picam2 = Picamera2()
picam2.start()
GPIO.setmode(GPIO.BCM)
IN1 = 21
IN2 = 20
IN3 = 16
IN4 = 12
ENA = 24
ENB = 23
motor = 17

GPIO.setup([IN1, IN2, IN3, IN4, ENA, ENB, motor], GPIO.OUT)

pwm = GPIO.PWM(motor, 20)
pwm.start(0)

pwmA = GPIO.PWM(ENA, 1000)
pwmB = GPIO.PWM(ENB, 1000)

pwmA.start(0)
pwmB.start(0)

def reverse():
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)

def forward():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)


def stop():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)

def left():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    pwmA.ChangeDutyCycle(70)
    pwmB.ChangeDutyCycle(10)

def right():
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)
    pwmA.ChangeDutyCycle(10)
    pwmB.ChangeDutyCycle(70)
    
def detect_line(gray):

    _, mask_black = cv2.threshold(gray, 70, 255, cv2.THRESH_BINARY_INV)
    return mask_black

def color_line(hsv):

    lower_yellow = np.array([20, 100, 100])
    upper_yellow = np.array([35, 255, 255])
    mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)

    lower_red1 = np.array([0, 100, 100])
    upper_red1 = np.array([10, 255, 255])

    lower_red2 = np.array([160, 100, 100])
    upper_red2 = np.array([180, 255, 255])

    mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask_red = mask_red1 + mask_red2
    
    return mask_red, mask_yellow

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

base_speed = 30
# Initialize PID variables
Kp = 0.7 # Proportional gain
Ki = 0.02 # Integral gain
Kd = 0.3 # Derivative gain
integral = 0
last_error = 0

frame_count = 0
N = 8

while True:
    frame = picam2.capture_array()
    frame = cv2.resize(frame, (320, 240))

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    cv2.imshow("Camera", frame)

    h, w = frame.shape[:2]

    # Detect masks
    mask_black = detect_line(gray)
    mask_red, mask_yellow = color_line(hsv)

    # Decide which line to follow
    black_score = np.sum(mask_black)
    red_score = np.sum(mask_red)
    yellow_score = np.sum(mask_yellow)
    
    if yellow_score:
        mask = mask_yellow

    elif red_score:
        mask = mask_red

    else:
        mask = mask_black

    # Find center
    y, x = np.where(mask == 255)

    if len(x) > 0:
        line_x = int(np.mean(x))
        frame_x = w // 2

        error = frame_x - line_x

        # PID
        P = Kp * error
        integral += error
        I = Ki * integral
        derivative = error - last_error
        D = Kd * derivative
        control = P + I + D
        last_error = error

        # Motor speeds
        left_speed  = max(0, min(100, base_speed - control))
        right_speed = max(0, min(100, base_speed + control))

        forward()
        pwmA.ChangeDutyCycle(right_speed)
        pwmB.ChangeDutyCycle(left_speed)
    
    frame_count += 1

    if frame_count % N == 0:
    
        symbol = detection(frame)
       
    if cv2.waitKey(1) == 27:
        break
        
pwm.stop()
GPIO.cleanup()
picam2.stop()
cv2.destroyAllWindows()