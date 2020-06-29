import cv2
def draw_circle(event, x, y, flags, param):
    global ix, iy, ex,ey,drawing, mode, cap, template, tempFlag
    if event == cv2.EVENT_LBUTTONDOWN:
        if not drawing:
            ix, iy = x,y
            drawing=True
    elif event == cv2.EVENT_LBUTTONUP:
        if drawing and tempFlag:
            ex,ey=x,y
            cv2.rectangle(img, (ix, iy), (x, y), (0, 255, 0), 1)
            tempFlag=False
            drawing=True
cv2.namedWindow('test')
cap=cv2.VideoCapture('rtsp://192.168.201.63/stream2')
_,img=cap.read()
drawing=False
tempFlag=True
cv2.setMouseCallback('test', draw_circle)
while True:
    #_,img=cap.read()
    cv2.imshow('test',img)
    key=cv2.waitKey(20)
    if key==27:
        break
cv2.destroyAllWindows()
print(ix,iy,ex,ey)
start_x=min(ix,ex)
end_x=max(ix,ex)
start_y=min(iy,ey)
end_y=max(iy,ey)
while True:
    _,img=cap.read()
    blur = cv2.GaussianBlur(img,(5,5),0)
    roi=img[start_y:end_y,start_x:end_x]
    roi_gray=cv2.cvtColor(roi,cv2.COLOR_BGR2GRAY)
    _,th=cv2.threshold(roi_gray,180,255,cv2.THRESH_OTSU+cv2.THRESH_BINARY_INV)
    cv2.imshow('roi',th)
    key=cv2.waitKey(20)
    if key==27:
        break
cv2.destroyAllWindows()
