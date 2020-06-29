
import cv2
import numpy as np

image2 = cv2.imread("2.jpg")
image1 = cv2.imread("1.jpg")
#cv2.imshow("Original",image)
#cv2.waitKey(0)
#图像image各像素减去50
#M = np.ones(image.shape,dtype="uint8")*50#与image大小一样的全50矩阵
img = cv2.absdiff(image1,image2)
cv2.imshow("Subtracted", img)
cv2.waitKey(0)