import cv2
rtsp_link='rtsp://192.168.200.2/stream2'
cap=cv2.VideoCapture(rtsp_link)
while True:
    rtv,img=cap.read()
    if rtv==False:
        cap=cv2.VideoCapture(rtsp_link)#重连
        continue
    else:
        cv2.imshow('',img)
    cv2.waitKey(20)

