import cv2
from picamera2 import Picamera2

picam2 = Picamera2()

# Configure camera for OpenCV (RGB format)
config = picam2.create_preview_configuration(main={"format": "BGR888", "size": (320, 240)})
picam2.configure(config)

picam2.start()

while True:
    frame = picam2.capture_array()   # get frame from camera
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) 
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    cv2.imshow("Camera", frame)      # show frame in OpenCV window
    
    if cv2.waitKey(1) == 27:         # press ESC to exit
        break

picam2.stop()
cv2.destroyAllWindows()
