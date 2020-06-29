import requests
import cv2
import datetime
import os
from random import randint
from time import time,ctime,sleep

def get_img_from_rtsp(ip,port='554'):
    cap = cv2.VideoCapture("rtsp://"+ip+':'+port+"/stream1")
    ret,img = cap.read()
    name=datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    cv2.imwrite(ip+'/'+name+'.jpg',img)
    cap.release()

def change_http_and_rtsp_port(ip,http_port,index):
    if index%2==1:
        new_rtsp_port='554'
    else:
        new_rtsp_port=str(randint(30000,31000))
    new_http_port=str(randint(32000,33000))
    url='http://'+ip+':'+http_port+'/?jcpcmd=portcfg -act set -rtsp '+new_rtsp_port+ ' -web '+new_http_port
    try:
        r=requests.get(url,cookies=dict(loginflag='1'))
    except:
        print('connect http port err')
    else:
        print("rtsp_port:{},http_port:{}".format(new_rtsp_port,new_http_port))
        print(r.text)
        return new_rtsp_port,new_http_port

ip=input('请输入IP:')
dir=ip
if not os.path.exists(dir):
    os.mkdir(dir)
http_port='80'
index=1    
while True:
    print('NO.%s'%(index))
    rtsp_port,http_port=change_http_and_rtsp_port(ip,http_port,index)
    sleep(15)
    get_img_from_rtsp(ip,rtsp_port)
    sleep(5)
    index+=1
    