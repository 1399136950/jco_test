import cv2
import os
import requests
from time import sleep
import datetime
import re



def get_video_info(ip,http_port):
    url='http://'+ip+':'+http_port+'/?jcpcmd=devvecfg -act list'
    try:
        r=requests.get(url,cookies=dict(loginflag='1'),timeout=1)
    except:
        return False,False
    else:
        # info_m=r.text.split('[Success]gnum=2;')[1].split('#')[0]
        # info_s=r.text.split('[Success]gnum=2;')[1].split('#')[1]
        info_m = re.split(r'\[Success\]gnum=\d+;', r.text)[1].split('#')[0]
        info_s = re.split(r'\[Success\]gnum=\d+;', r.text)[1].split('#')[1]
        m={}
        s={}
        for i in info_m.split(';'):
            if len(i)>0:
                m[i.split('=')[0]]=i.split('=')[1]
        for i in info_s.split(';'):
            if len(i)>0:
                s[i.split('=')[0]]=i.split('=')[1]
        return m,s

        
def send_request(ip,http_port):
    urls=[
        "vgrect -act set -timestrategy 0:2164260863,1:2164260863,2:2164260863,3:2164260863,4:2164260863,5:2164260863,6:2164260863, -enable 1 -thresh 50 -indoor 0 -dir 2 -blink 1 -y0 0 -y1 0 -y2 1076 -y3 1076 -x0 0 -x1 1916 -x2 1916 -x3 0",
        'videomaskcfg -act set -maskid 0 -masken 1 -color 0  -left 0 -top 257 -right 123 -bottom 349',
        'videomaskcfg -act set -maskid 1 -masken 1 -color 0  -left 740 -top 477 -right 864 -bottom 569',
        'videomaskcfg -act set -maskid 2 -masken 1 -color 0  -left 1182 -top 305 -right 1306 -bottom 397',
        'videomaskcfg -act set -maskid 3 -masken 1 -color 0  -left 1393 -top 546 -right 1517 -bottom 638',
        'osdcfg -act set  -nameen 1 -nameleft 1098 -nametop 1052 -name "HSIPC安送朵花地方和不麻烦您吗个女孩们才处女宠环风格会没出过和每次帮" -osdlanguage 0'
    ]
    for u in urls:
        url='http://'+ip+':'+http_port+'/?jcpcmd='+u
        #print(url)
        for i in range(5):
            try:
                r=requests.get(url,cookies=dict(loginflag='1'),timeout=3)
            except:
                pass
            else:
                print(r.text)
                break

        
def set_video_size(ip,http_port,vsize,code_type,video_id):
    if video_id=='0':
        if vsize=='7' or vsize=='2':
            set_video_size(ip,http_port,'1',code_type,'1')
    url='http://'+ip+':'+http_port+'/?jcpcmd=devvecfg -act set -id ' + video_id + ' -vencsize '+vsize +' -codec ' + code_type
    try:
        r=requests.get(url,cookies=dict(loginflag='1'),timeout=1)
    except:
        return False
    else:
        return r.text

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
            w = cap.get(3)
            h = cap.get(4)
            cv2.imwrite(ip+'/'+img_name+'.jpg',img)
            print(' ',w,'*',h)
            cap.release()
            return True
        else:
            print("can't read image")
            return False

def wait_until_boot(ip,http_port,time,res_data):
    for i in range(time):
        sleep(10)
        m,s=get_video_info(ip,http_port)
        if m and s:
            #print("m",m)
            #print("s",s)
            if m['vencsize']== res_data['0'][0] and m['codec']==res_data['0'][1] and s['vencsize']== res_data['1'][0] and s['codec']==res_data['1'][1]:
                break
        else:
            pass
    

if __name__ == '__main__':    
    str2vsize={
        '1':'CIF',
        '2':'D1',
        '3':'720P',
        '5':'1080P',
        '6':'QVGA',
        '7':'VGA',
        '8':'960P',
        '9':'3M',
        '11': '360P',
        '12':'4M',
        '13':'5M',
        '15':'8M'#4K分辨率
    }
    video_lists={
        '15': ['2','3','5','7','8','9','12','13','15'],       #8M
        '13': ['2','3','5','7','8','9','12','13'],            #5M
        '12': ['2','3','5','7','8','9','12'],                 #4M
        '9' : ['2','3','5','7','8','9'],                      #3M
        '5' : ['2','3','5','7','8']                           #2M
    }

    str2CodeType={
        '2':'H264',
        '7':'H265'
    }

    ip = input('请输入IP:')

    http_port = input('http_port:')
    if http_port == '':
        http_port = '80'

    have_mjpeg = False
    ans = input('是否有第三码流:')
    if ans == 'y' or ans == 'Y':
        have_mjpeg = True

    send_request(ip, http_port)

    dir = ip

    if not os.path.exists(dir):
        os.mkdir(dir)
        
    video_info_m, video_info_s = get_video_info(ip, http_port)
    print(video_info_m)

    size_lists = video_lists[video_info_m['vencsize']]#主码流
    # print(size_lists)

    size_lists_sub = ['1','2','6','7', '11']#子码流
    code_type = video_info_m['codec']#编码类型

    if code_type == '2':
        code_lists = ['2']
    elif code_type == '7':
        code_lists = ['2','7']

    for i in size_lists:
        if i == '2' or i == '7':#D1
            tmp=list(size_lists_sub)
            if i == '2':#D1
                tmp.remove('2')
            elif i == '7':#VGA
                tmp.remove('2')
                tmp.remove('7')
            for j in tmp:
                for m in code_lists:
                    for n in code_lists:
                        print(str2vsize[i], m, str2vsize[j],n)
                        
                        set_video_size(ip, http_port, i, m, '0')#主
                        set_video_size(ip, http_port, j, n, '1')#从
                        wait_until_boot(ip, http_port, 5, {'0':[i,m],'1':[j,n]})
                        m_img_name = 'M_'+str2vsize[i]+'_'+str2vsize[i]+'_'+str2CodeType[m]+'_'+str2vsize[j]+'_'+str2CodeType[n]
                        s_img_name = 'S_'+str2vsize[j]+'_'+str2vsize[i]+'_'+str2CodeType[m]+'_'+str2vsize[j]+'_'+str2CodeType[n]
                        mjpg_img_name = 'MJPEG_'+str2vsize[j]+'_'+str2vsize[i]+'_'+str2CodeType[m]+'_'+str2vsize[j]+'_'+str2CodeType[n]
                        
                        for iter_numi in range(3):
                            rtv = get_img_from_rtsp(ip, m_img_name, 'stream1')
                            if not rtv:
                                sleep(15)
                            else:
                                break
                        if not rtv:
                            exit(0)
                        
                        for iter_num in range(3):
                            rtv = get_img_from_rtsp(ip, s_img_name, 'stream2')
                            if not rtv:
                                sleep(15)
                            else:
                                break
                        if not rtv:
                            exit(0)
                        '''读取MJPG流'''   
                        if have_mjpeg:
                            for iter_num in range(3):
                                rtv = get_img_from_rtsp(ip, mjpg_img_name, 'stream3')
                                if not rtv:
                                    sleep(15)
                                else:
                                    break
                            if not rtv:
                                exit(0)
        else:
            for j in size_lists_sub:
                for m in code_lists:
                    for n in code_lists:
                        print(str2vsize[i], m, str2vsize[j], n)
                        set_video_size(ip, http_port, i, m, '0')#主
                        set_video_size(ip, http_port, j, n, '1')#从
                        #wait_until_boot(ip,http_port,5)
                        wait_until_boot(ip, http_port, 5, {'0':[i,m],'1':[j,n]})
                        m_img_name = 'M_'+str2vsize[i]+'_'+str2vsize[i]+'_'+str2CodeType[m]+'_'+str2vsize[j]+'_'+str2CodeType[n]
                        s_img_name = 'S_'+str2vsize[j]+'_'+str2vsize[i]+'_'+str2CodeType[m]+'_'+str2vsize[j]+'_'+str2CodeType[n]
                        mjpg_img_name = 'MJPEG_'+str2vsize[j]+'_'+str2vsize[i]+'_'+str2CodeType[m]+'_'+str2vsize[j]+'_'+str2CodeType[n]
                        
                        for iter_num in range(3):
                            rtv = get_img_from_rtsp(ip, m_img_name, 'stream1')
                            if not rtv:
                                sleep(15)
                            else:
                                break
                        if not rtv:
                            exit(0)
                            
                        for iter_num in range(3):
                            rtv =  get_img_from_rtsp(ip, s_img_name, 'stream2')
                            if not rtv:
                                sleep(15)
                            else:
                                break
                        if not rtv:
                            exit(0)
                        '''读取MJPG流'''   
                        if have_mjpeg:
                            for iter_num in range(3):
                                rtv = get_img_from_rtsp(ip, mjpg_img_name, 'stream3')
                                if not rtv:
                                    sleep(15)
                                else:
                                    break
                            if not rtv:
                                exit(0)
    #还原分辨率
    set_video_size(ip, http_port, video_info_m['vencsize'], video_info_m['codec'], '0')#主
    set_video_size(ip, http_port, video_info_s['vencsize'], video_info_s['codec'], '1')#从

