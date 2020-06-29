import cv2
import numpy as np
import matplotlib.pyplot as plt

def show_imgs(img_list):
    str_lists=['sobelX','threshold','close','res']
    for i in range(len(img_list)):
        plt.subplot(2,2,i+1)
        plt.title(str_lists[i])
        plt.imshow(img_list[i])
    plt.show()

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

img_name=input('img_name:')
img=cv2.imread(img_name)
kernel = np.ones((11,11),np.uint8)
blur=cv2.GaussianBlur(img,(3,3),0)#高斯模糊
img_gray=cv2.cvtColor(blur,cv2.COLOR_BGR2GRAY)#灰阶
sobelx = cv2.Sobel(img_gray,cv2.CV_16S, 1, 0)#对x求导
sobel=cv2.convertScaleAbs(sobelx);#转换图像位数
_,th=cv2.threshold(sobel,0,255,cv2.THRESH_OTSU)#二值化
img_close=cv2.morphologyEx(th,cv2.MORPH_CLOSE,kernel)#闭操作
im2,contours,hierarchy = cv2.findContours(img_close, 1, 2)#寻找边框
for cnt in contours:
    rect = cv2.minAreaRect(cnt)
    box = cv2.boxPoints(rect)
    box = np.int0(box)
    if getMaxDistance(box):#x距离大于y距离
        distance_list=[]
        for i in range(1,len(box)):
            distance_list.append(get_distance(box[0],box[i]))
        width=min(distance_list)
        distance_list.remove(width)
        length=min(distance_list)
        distance_list.remove(length)
        if (width*length)<1500:#面积太小的矩形pass
           pass
        else:
            if width/length>=0.2 and width/length<=0.5:#在此比例之间
                cv2.drawContours(img,[box],0,(0,255,0),1)#画正接矩形


img_rgb=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
img_lists=[sobel,th,img_close,img_rgb]
show_imgs(img_lists)


