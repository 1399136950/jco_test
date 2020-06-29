import cv2
font = cv2.FONT_HERSHEY_SIMPLEX
IP=input("请输入IP:");
username=input("请输入用户名:");
password=input("请输入密码:");
if(username=='' and password==''):
    cap = cv2.VideoCapture("rtsp://"+IP+"/stream2")
else:
    cap = cv2.VideoCapture("rtsp://"+username+':'+password+'@'+IP+"/stream2")
print('已连接')
face_cascade=cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
while (1):
    ret,img = cap.read()
    gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    faces=face_cascade.detectMultiScale(gray,1.3,5)
    #faces=face_cascade.detectMultiScale(gray,1.3,5)
    for (x,y,h,w) in faces:
        img=cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
    img =cv2.putText(img, '', (123,456), font, 2, (0,255,0), 3) 
    cv2.imshow('facedected',img)
    #cv2.imwrite('faces.jpg',img)
    cv2.waitKey(40)

