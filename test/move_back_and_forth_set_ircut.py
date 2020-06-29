from time import sleep,strftime,time
from cv2 import VideoCapture,imwrite
import re

from comparison_image_effect import *


if __name__ == '__main__':
    ip = input('请输入IP地址:')
    sleep_time = input('休息间隔:')
    if sleep_time == '':
        sleep_time = 15
    else:
        sleep_time = int(sleep_time)
    res = re.match('(?:\d+\.){3}\d+$', ip)
    if res == None:
        raise Exception('地址格式错误')

    mkdir(ip)
    now_time=strftime('%Y-%m-%d_%H-%M-%S')
    mkdir(ip+'/'+now_time)
    path=ip+'/'+now_time+'/'
    index=1

    if get_device_type(ip) == '1':  #红外版本
        ircut_type = ['2','3']
        

    
    elif get_device_type(ip) == '3':    #软光敏版本
        ircut_type = ['4','5']
        
    while 1:
        print(index)
        set_ircut_mode(ip, ircut_type[index%2])  #软光敏-彩色
        
        sleep(sleep_time)
        if get_img_from_rtsp(ip, 'M_{}'.format(index), 'stream1', path):  #获取主码流
            print("save Master image success")
        if get_img_from_rtsp(ip, 'S_{}'.format(index), 'stream2', path):  #获取子码流
            print("save Slave image success")
        # set_ircut_mode(ip, '4')  #软光敏-彩色
        sleep(1)
        index += 1



