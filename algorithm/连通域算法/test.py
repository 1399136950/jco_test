import cv2
import numpy as np
img=cv2.imread('test.jpg',0)
rows,columns=img.shape
maps=np.zeros([rows,columns])
for r in range(rows):
    for c in range(columns):
        print(img[r][c])