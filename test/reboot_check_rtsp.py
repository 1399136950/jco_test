import cv2
import requests
from time import sleep,time
import os
import re

from comparison_image_effect import get_version, get_device_type, set_ircut_mode



def reboot(ip):
    url='http://'+ip+'/?jcpcmd=sysctrl -act set -cmd 0'
    try:
        r=requests.get(url,cookies=dict(loginflag='1'),timeout=20)
    except:
        return False
    else:
        return True
        
def set_color(ip, device_type):
    if device_type == '1':  #红外
        set_ircut_mode(ip, '3')
    elif device_type == '3':    #软光敏
        set_ircut_mode(ip, '4')
    
def set_blackWhile(ip, device_type):
    if device_type == '1':
        set_ircut_mode(ip, '2')
    elif device_type == '3':
        set_ircut_mode(ip, '5')

  
if __name__ == '__main__':        

    device_types={
        '1': '红外',
        '2': '黑光',
        '3': '软光敏'
    }

    ip = input('输入ip:')
    dir = ip
    
    device_type = get_device_type(ip)
    print('device_type', device_types[device_type])
    # exit(0)

    sleep_time = int(input('输入间隔时间:'))
    
    ans = input('是否存在第三码流:')
    if ans == 'y' or ans == 'Y':
        have_mjpeg = True
    else:
        have_mjpeg = False

    if not os.path.exists(dir):
        os.mkdir(dir)

    index = 1

    while True:
        print('NO.{}'.format(index))
        if reboot(ip):
            sleep(sleep_time)

            cap_slave=cv2.VideoCapture('rtsp://'+ip+'/stream2')
            cap_master=cv2.VideoCapture('rtsp://'+ip+'/stream1')
            if have_mjpeg:
                cap_mjpeg = cv2.VideoCapture('rtsp://'+ip+'/stream3')
            if cap_slave.isOpened()==False or cap_master.isOpened()==False:
                print('No Rtsp Stream')
                break
            else:
                try:
                    rt_m, master = cap_master.read()
                    rt_s, slave = cap_slave.read()
                    if have_mjpeg:
                        rt_mjpeg, mjpeg = cap_mjpeg.read()
                except:
                    print('read frame err!')
                else:
                    if rt_m and rt_s:
                        master_name = dir + '/' + str(index) + '_master.jpg'
                        slave_name = dir + '/' + str(index) + '_slave.jpg'
                        cv2.imwrite(master_name, master)
                        cv2.imwrite(slave_name, slave)
                        if have_mjpeg:
                            if rt_mjpeg:
                                mjpeg_name = dir + '/' + str(index) + '_mjpeg.jpg'
                                cv2.imwrite(mjpeg_name, mjpeg)
                            else:
                                print('No mjpeg stream')
                    else:
                        if not rt_m:
                            print("No master stream")
                        if not rt_s:
                            print("No slave stream")
                        break
            cap_slave.release()
            cap_master.release()
            if have_mjpeg:
                cap_mjpeg.release()
            if index % 2 == 0:
                set_color(ip, device_type)
            else:
                set_blackWhile(ip, device_type)
            
            index+=1
        else:
            print('Send Cmd Error')
            break

    cap_slave.release()
    cap_master.release()
    if have_mjpeg:
        cap_mjpeg.release()
