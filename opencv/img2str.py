import cv2
img=cv2.imread('1.png',0)
tmp=cv2.resize(img,(0,0),fx=0.2,fy=0.2,interpolation=cv2.INTER_NEAREST)
rt,tmp=cv2.threshold(tmp,128,255,cv2.THRESH_BINARY)
fd=open('1.txt','a+')
for line in tmp:
    str_line=''
    for pxl in line:
        if pxl==0:
            str_line=str_line+'1'
        else:
            str_line=str_line+'0'
    fd.write(str_line)
    fd.write("\n")
fd.close()
    
        
