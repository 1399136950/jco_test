import cv2
import numpy as np
cap=cv2.VideoCapture('rtsp://192.168.183.24/stream2')
kernel = np.ones((3,3),np.uint8)
rt1,frame1=cap.read()
rt2,frame2=cap.read()
frm1_gray=cv2.cvtColor(frame1,cv2.COLOR_BGR2GRAY)
frm2_gray=cv2.cvtColor(frame2,cv2.COLOR_BGR2GRAY)
_,th1=cv2.threshold(frm1_gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
_,th2=cv2.threshold(frm2_gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
while True:
    _,frame_now=cap.read()
    frm_now_gray=cv2.cvtColor(frame_now,cv2.COLOR_BGR2GRAY)
    _,th_now=cv2.threshold(frm_now_gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    th_now = cv2.dilate(th_now,kernel,iterations = 1)#膨胀
    th1 = cv2.dilate(th1,kernel,iterations = 1)#膨胀
    th2 = cv2.dilate(th2,kernel,iterations = 1)#膨胀
    det1=cv2.absdiff(th2,th1)
    det2=cv2.absdiff(th_now,th2)
    img1_bg = cv2.bitwise_and(det1,det2)
    #blru=cv2.medianBlur(img1_bg,5)#中值滤波

    binary , contours, hierarchy = cv2.findContours(img1_bg,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)#寻找边框
    cv2.drawContours(frame_now,contours,-1,(0,255,0),1)#划线
    th1,th2=th2,th_now
    cv2.imshow('2',th1)
    cv2.imshow('1',th2)
    ket=cv2.waitKey(10)
    if ket==27:
        break
cap.release()
cv2.destroyAllWindows()
