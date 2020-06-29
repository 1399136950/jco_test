import cv2
def draw_circle(event, x, y, flags, param):
    global l,drawing
    if event == cv2.EVENT_LBUTTONDOWN:
        if not drawing:
            l.append([x,y])
            
            print('press')
            if len(l)==4:
                drawing=True
    elif event == cv2.EVENT_LBUTTONUP:
        pass
        print('up')
l=[]
drawing=False
cv2.namedWindow('test')
cv2.setMouseCallback('test', draw_circle)
img=cv2.imread('11.jpg')
while True:
    cv2.imshow('test',img)
    if cv2.waitKey(10)==27:
        break
