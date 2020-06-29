import cv2
import os

for file in os.listdir('tmp'):
    img=cv2.imread('tmp/'+file,0)
    '''
    height,width=img.shape
    status={}
    start=[]
    end=[]
    model='start'
    for column in range(width):
        status[column]=0
        for line in range(height):
            if img[line][column] == 0:
                status[column]=1
        if column>=1:
            if status[column-1]==status[column]:
                pass
            else:
                if model=='start':
                    start.append(column)
                    model='end'
                else:
                    end.append(column)
                    model='start'
    print(start)
    print(end)
    for i in range(len(start)):
        if i >=1 and i < len(start)-1:
                if end[i]-start[i-1] >=6 and start[i]-end[i-1] <=3:
                    start.remove(start[i])
                    end.remove(end[i-1])
    print(start)
    print(end)
    name=file.split('.')[0]
    for i in range(len(start)):
        tmp=img[0:,start[i]:end[i]]
        tmp_file=name+'_'+str(i)+'.png'
        cv2.imwrite('res/'+tmp_file,tmp)
    '''
    pix_len=20
    name=file.split('.')[0]
    for i in range(1,5):
        tmp=img[0:,(i-1)*pix_len:i*pix_len]
        try:
            type=name[i-1]
        except:
            print(name)
        else:
            tmp_file=type+'_'+name+'.png'
            cv2.imwrite('res/'+type+'/'+tmp_file,tmp)
    
    
