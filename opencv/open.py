import cv2
import numpy as np
original_img = cv2.imread('33_tmp.png',0)
kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(2,2))
opened1 = cv2.morphologyEx(original_img, cv2.MORPH_OPEN, kernel,iterations=1)

cv2.imshow("open",opened1)
closed1 = cv2.morphologyEx(opened1, cv2.MORPH_CLOSE, kernel,iterations=1)
cv2.imshow("close",closed1)
cv2.waitKey(0)
