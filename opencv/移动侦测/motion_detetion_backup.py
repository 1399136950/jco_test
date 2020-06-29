import cv2
import numpy as np



def get_distance(point1,point2):#计算两点间距离
    res=0
    for i in range(len(point1)):
        res=res+(point1[i]-point2[i])**2
    return res**0.5

def getMaxDistance(box):#获取最大垂直间距和最大水平间距
    x_list=[]
    y_list=[]
    for i in range(len(box)):
        x_list.append(box[i][0])
        y_list.append(box[i][1])
    x_d=max(x_list)-min(x_list)
    y_d=max(y_list)-min(y_list)

    if x_d>y_d:
        return True
    else:
        return False


cap=cv2.VideoCapture('rtsp://user:user@192.168.201.15/stream2')
kernel = np.ones((5,5),np.uint8)
rt,frame1=cap.read()
frm1_gray=cv2.cvtColor(frame1,cv2.COLOR_BGR2GRAY)
rt,th1=cv2.threshold(frm1_gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
index=0
while True:
    rt1,frame2=cap.read()
    if rt1:
        frm2_gray=cv2.cvtColor(frame2,cv2.COLOR_BGR2GRAY)
        rt,th2=cv2.threshold(frm2_gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)#自适应阈值化
        tmp= cv2.absdiff(th2,th1)#差值
        #cv2.imshow('tmp',tmp)#显示图像
        blru=cv2.medianBlur(tmp,5)#中值滤波
        th1=th2
        dilation = cv2.dilate(blru,kernel,iterations = 10)#膨胀
        erode = cv2.erode(dilation,kernel,iterations = 5)#腐蚀
        #cv2.imshow('motion erode',erode)#显示图像
        binary , contours, hierarchy = cv2.findContours(erode,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)#寻找边框
        
        for cnt in contours:
            rect = cv2.minAreaRect(cnt)
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            #if getMaxDistance(box):#x距离大于y距离
                #pass
            #else:
            cv2.drawContours(frame2,[box],0,(0,255,0),1)
        
        #cv2.drawContours(frame2,contours,-1,(0,255,0),1)#划线
        cv2.imshow('motion detection',frame2)#显示图像
        ket=cv2.waitKey(10)
        if ket==27:
            break
cap.release()
cv2.destroyAllWindows()
