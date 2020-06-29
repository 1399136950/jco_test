import cv2
import numpy as np
img=cv2.imread('test.jpg')
l,c,t=img.shape
newimg=np.zeros([l*2,c*2,t])
for i in range(l):
    for j in range(c):
        new_l=i*2
        new_c=j*2
        newimg[new_l][new_c]=img[i][j]
        newimg[new_l][new_c+1]=img[i][j]
        newimg[new_l+1][new_c]=img[i][j]
        newimg[new_l+1][new_c+1]=img[i][j]
cv2.imwrite('new.jpg',newimg)

