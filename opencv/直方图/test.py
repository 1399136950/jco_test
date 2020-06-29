import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt
img = cv.imread('test.jpg',0)
equ = cv.equalizeHist(img)
# res = np.hstack((img,equ)) #stacking images side-by-side
cv.imshow('res.png',equ)

cv.waitKey(0)
