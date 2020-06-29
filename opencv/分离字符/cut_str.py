import cv2
import numpy as np
img=cv2.imread('th.png',0)
img_t=img.T
res=[]
model='start'
lists={
    'start':[],
    'end':[]
}
for i in range(len(img_t)):
    for pxl in img_t[i]:
        if pxl==0:
            res.append(i)#记录有像素的列
            break
    if len(res)<=0:
        if i in res:
            lists['start'].append(i)
    else:
        if i-1 not in res:#前一行无像素
            if i in res:#当前行有
                lists['start'].append(i)
            else:
                pass
        else:#前一行有
            if i in res:#当前也有
                pass
            else:
                lists['end'].append(i-1)
for i in range(len(lists['end'])):
    tmp=img[0:,lists['start'][i]:lists['end'][i]+1]
    cv2.imwrite(str(i)+'.jpg',tmp)
                
            

    
        

            
