import cv2
import numpy as np
cap=cv2.VideoCapture('rtsp://192.168.183.24/stream2')

while True:
    rt,img=cap.read()
    #gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    blur=cv2.blur(img,(5,5))
    cv2.imshow('',blur)
    cv2.imshow('1',img)
    #break
    key=cv2.waitKey(1)
    if key==27:
        break
cap.release()
cv2.destroyAllWindows()
