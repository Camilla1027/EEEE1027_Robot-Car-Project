import RPi.GPIO as GPIO
import time
import cv2

from picamera2 import Picamera2
import numpy as np

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

pwm = GPIO.PWM(motor, 50)
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
    pwmA.ChangeDutyCycle(90)
    pwmB.ChangeDutyCycle(10)

def right():
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)
    pwmA.ChangeDutyCycle(10)
    pwmB.ChangeDutyCycle(90)
    
def detect_line(hsv):
    
    lower = np.array([0, 0, 0])
    upper = np.array([180, 255, 70])
    mask = cv2.inRange(hsv, lower, upper)
    
    return mask
base_speed = 50
# Initialize PID variables
Kp = 0.7 # Proportional gain
Ki = 0.02 # Integral gain
Kd = 0.3 # Derivative gain
integral = 0
last_error = 0

while True:
    image = picam2.capture_array()
    image = cv2.resize(image, (320, 240))

    h, w = image.shape[:2]
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    line_mask = detect_line(hsv)
    cv2.imshow("Camera", image)

    y, x = np.where(line_mask == 255) #find position of the line
    
    line_x = np.mean(x) #center of the line(x)
    frame_x = w//2 #center of the frame(x)
    
    if len(x)>0:
        
        # Calculate error
        error = frame_x - line_x
        
        # PID calculation
        P = Kp * error
        integral += error
        I = Ki * integral
        derivative = error - last_error
        D = Kd * derivative
        control = P + I + D
        last_error = error
        
        # Apply to motors
        left_speed  = max(0, min(100, base_speed - control))
        right_speed = max(0, min(100, base_speed + control))
        
        if abs(error) > 100:
            if error > 0:
                left()
            else:
                right()
        else:
            forward()
            pwmA.ChangeDutyCycle(right_speed)
            pwmB.ChangeDutyCycle(left_speed)
    
    else:
        while line_x == frame_x:
            reverse()
        
    if cv2.waitKey(1) == 27: 
        break

pwm.stop()
GPIO.cleanup()
picam2.stop()
cv2.destroyAllWindows()