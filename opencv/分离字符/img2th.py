import cv2
img=cv2.imread('33.png',0)
_,th=cv2.threshold(img,0,255,cv2.THRESH_OTSU)
cv2.imwrite('th.png',th)
