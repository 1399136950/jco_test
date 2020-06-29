import cv2
import re
import os

def get_img_num(num):
    l=3-len(str(num))
    imgname='0'*l+str(num)+'.jpg'
    return imgname   

def cut_img(imgname,dirname):
    index=re.findall('0*(\d+)',imgname)[0]
    img=cv2.imread(imgname)
    height,width,channel=img.shape
    width_half=int(width/2)
    img1=img[0:,0:width_half]
    img2=img[0:,width_half:]
    name1=get_img_num(int(index)*2-1)
    name2=get_img_num(int(index)*2)
    cv2.imwrite(dirname+'/'+name1,img1)
    cv2.imwrite(dirname+'/'+name2,img2)

def scan_dir(dirname):
    newdirname=dirname+'-new'
    mkdir(newdirname)
    for filename in os.listdir(dirname):
        cut_img(dirname+'/'+filename,newdirname)

def mkdir(dirname):
    if os.path.exists(dirname):
        pass
    else:
        os.mkdir(dirname)

if __name__=='__main__':
    dirname=input('输入文件夹名:')
    scan_dir(dirname)
