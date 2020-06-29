import cv2
import os
import requests
from time import sleep
import datetime



def get_img_from_rtsp(ip,img_name,stream_type,port='554'):
    try:
        cap = cv2.VideoCapture("rtsp://"+ip+':'+port+"/"+stream_type)
    except:
        print('RTSP ERROR')
        return False
    else:
        i=0
        while i<5:
            ret,img = cap.read()
            i+=1
        if ret:
            w=cap.get(3)
            h=cap.get(4)
            cv2.imwrite(ip+'/'+img_name+'.jpg',img)
            print(' ',w,'*',h)
            cap.release()
            return True
        else:
            print("can't read image")
            return False


index=1
ip='192.168.201.63'
if not os.path.exists(ip):
    os.mkdir(ip)
urls=['devvecfg -act set -id 0 -vencsize 3','devvecfg -act set -id 0 -vencsize 15']
while True:
    print('No.',index)
    url='http://'+ip+'/?jcpcmd='+urls[index%2]
    try:
        r=requests.get(url,cookies=dict(loginflag='1'))
    except:
        print('requests err')
        break
    else:
        sleep(30)
        img_name1=str(index)+'_M'
        img_name2=str(index)+'_S'
        r1=get_img_from_rtsp(ip,img_name1,'stream1',port='554')
        r2=get_img_from_rtsp(ip,img_name2,'stream2',port='554')
        if r1 and r2:
            index+=1
        else:
            break
        
    
    
