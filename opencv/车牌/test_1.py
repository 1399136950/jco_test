import cv2
import numpy as np
import matplotlib.pyplot as plt

def show_imgs(img_list):
    str_lists=['blur','sobelX','threshold','close','res']
    for i in range(len(img_list)):
        plt.subplot(3,2,i+1)
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

_,th=cv2.threshold(img_gray,0,255,cv2.THRESH_OTSU)
canny=cv2.Canny(img_gray, 50,150)


