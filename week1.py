import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

IN1 = 21
IN2 = 20
IN3 = 16
IN4 = 12
ENA = 24
ENB = 23
motor = 17

GPIO.setup([IN1, IN2, IN3, IN4, ENA, ENB, motor], GPIO.OUT)

pwmA = GPIO.PWM(ENA, 255)
pwmB = GPIO.PWM(ENB, 255)

pwmA.start(90)
pwmB.start(90)

def forward():
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    
def reverse():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)

def stop():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)

def right():
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)
    pwmA.ChangeDutyCycle(0)
    pwmB.ChangeDutyCycle(95)
    
def left():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    pwmB.ChangeDutyCycle(0)
    pwmA.ChangeDutyCycle(95)
    
def angle():
    angle=float(input("Angle: "))
    delay=7.53*10**-3*angle+0.19
    return delay

def rotation():
    choice=input("1 for right,  2 for left: ")
    if choice== "1":
        return 1
    elif choice == "2":
        return 2
        
    
delay=angle()
choice=rotation()

if choice == 1:
    right()
else:
    left()
    

time.sleep(delay)
stop()