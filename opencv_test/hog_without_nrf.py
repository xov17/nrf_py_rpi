from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np
import sys, signal
def signal_handler(signal, frame):
	print("\nprogram terminated")
	sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

camera = PiCamera()

time.sleep(0.1)

rawCapture = PiRGBArray(camera)
camera.capture(rawCapture, format="bgr")
img = rawCapture.array
start = time.time()
win_size = (64, 128)
img = cv2.resize(img, win_size)
img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
hog = cv2.HOGDescriptor()
h = hog.compute(img)
end = time.time()
print 'time: ', (end-start), 'seconds'
