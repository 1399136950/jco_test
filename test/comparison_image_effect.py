import socket
import requests
import os
import re
from cv2 import VideoCapture,imwrite
from time import sleep,strftime,time
from functools import wraps

from mp4recoder import AvcRecoder, HevcRecoder


def is_newLightCtrl(ip):    # 是否新补光协议
    url = 'http://' + ip + '/?jcpcmd=lightextcfg -act list'
    try:
        r = requests.get(url, timeout=5, cookies={'loginflag': '1'})
    except Exception as e:
        raise Exception(e)
    else:
        if r.status_code == 200:
            info = r.text.strip('\r\n')
            if re.match(r'^szJcpResult="\[Success\].*$', info):
                '''
                devtype:
                    0 红外灯；
                    1 白光灯、星光；
                    2 双光源
                irswitchmode:
                    1 使用光敏获取 LUX 值 (光敏模式)
                    2 摄像机算法获取 LUX 值(软光敏模式)
                    3 用户设置的 夜间时间(日夜模式),
                '''
                devtype = re.findall('devtype=(\d+);', info)[0]
                irswitchmode = re.findall('irswitchmode=(\d+);', info)[0]
                return (devtype, irswitchmode)
            else:
                return False

def get_device_type(ip)->str:
    '''
    设备类型:
        '1'是红外,
        '2'是黑光,
        '3'是软光敏,
        '4'是旧红外
    '''
    
    LightCtrlType = is_newLightCtrl(ip) # False为老版本,否则为新版本
    
    if LightCtrlType:   # 新补光协议参数
        devtype, irswitchmode = LightCtrlType
        if devtype == '0' or devtype == '2':  # 红外or双光源
            if irswitchmode == '1': # 硬光敏
                return '1'
            elif irswitchmode == '2':   # 软光敏
                return '3'
        elif devtype == '1':  # 白光灯、星光
            return '2'
        else:
            raise Exception('unknow device_type')
    else:   # 老补光协议
        version = get_version(ip)
        if version:
            if re.match('^[VT]BA?\d+.*?', version):   #   黑光
                return '2'
            elif re.match('^[VT]A?\d+.*?', version):   #   红外
                return '1'
            elif re.match('^[VT]CA?\d+.*?', version):   #   软光敏1
                return '3'
            elif re.match('^VCFA?\d+.*?', version):   #   汉邦定制红外
                return '1'
            else:
                raise Exception('unknow device_type')
        else:
            raise Exception('get device_type timeout')

def get_video_info(ip,http_port):
    url='http://'+ip+':'+http_port+'/?jcpcmd=devvecfg -act list'
    try:
        r=requests.get(url,cookies=dict(loginflag='1'),timeout=1)
    except:
        return False,False
    else:
        info_m=r.text.split('[Success]gnum=2;')[1].split('#')[0]
        info_s=r.text.split('[Success]gnum=2;')[1].split('#')[1]
        m={}
        s={}
        for i in info_m.split(';'):
            if len(i)>0:
                m[i.split('=')[0]]=i.split('=')[1]
        for i in info_s.split(';'):
            if len(i)>0:
                s[i.split('=')[0]]=i.split('=')[1]
        return m,s

def log(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        s=time()
        res=func(*args,**kwargs)
        end=time()
        print('[{}][Runtime:{:.4f}s]'.format(func.__name__,end-s))
        return res
    return wrapper

def mkdir(dirname): # 创建文件夹
    if os.path.exists(dirname):
        pass
    else:
        os.mkdir(dirname)
        
@log
def upgrade(ip,file):   # 上传升级包
    sk = socket.socket(socket.AF_INET,socket.SOCK_STREAM,0)
    try:
        sk.connect((ip,8006))
    except:
        sleep(10)
        print("sleep 10")
        sk.connect((ip,8006))
    finally:
        file = open(file,'rb')
        a = file.read()
        file.close()
        sk.send(a)
        sk.close()
        print('upload file success')

def get_video_info(ip,http_port):
    url='http://'+ip+':'+http_port+'/?jcpcmd=devvecfg -act list'
    try:
        r=requests.get(url,cookies=dict(loginflag='1'),timeout=1)
    except:
        return False
    else:
        info_m=r.text.split('[Success]gnum=2;')[1].split('#')[0]
        info_s=r.text.split('[Success]gnum=2;')[1].split('#')[1]
        m={}
        s={}
        for i in info_m.split(';'):
            if len(i)>0:
                m[i.split('=')[0]]=i.split('=')[1]
        for i in info_s.split(';'):
            if len(i)>0:
                s[i.split('=')[0]]=i.split('=')[1]
        return m,s

def set_video_size(ip,vsize,video_id):
    url='http://'+ip+'/?jcpcmd=devvecfg -act set -id ' + video_id + ' -vencsize '+ vsize
    try:
        r=requests.get(url,cookies=dict(loginflag='1'),timeout=1)
    except:
        return False
    else:
        return r.text        

def wait_until_boot(ip,time):
    for i in range(time):
        sleep(10)
        if get_video_info(ip,http_port=80):
            break
        else:
            pass

def check_video_size(ip):
    str2vsize={
        '2160':'15',
        '1944':'13',
        '1920':'13',
        '1440':'12',
        '1296':'9',
        '1536':'9',
        '1152':'9',
        '1296':'9',
        '1080':'5'
    }
    url='http://'+ip+'/?jcpcmd=bootargs -act list'
    url1='http://'+ip+'/?jcpcmd=devvecfg -act list'
    r=requests.get(url,cookies=dict(loginflag='1'))
    r1=requests.get(url1,cookies=dict(loginflag='1'))
    max_height=re.findall('maxheight=(\d+)',r.text)[0]
    now_size=re.findall('vencsize=(\d+)',r1.text)[0]
    if str2vsize[max_height] == now_size:
        pass
    else:
        print('change video size now')
        set_video_size(ip,str2vsize[max_height],'0')
        sleep(10)
        wait_untile_upgrade_success(ip)
            

def get_upgrade_progress(ip):   # 获取升级进度
    try:
        r=requests.get('http://'+ip+'/?jcpcmd=update -act list',cookies=dict(loginflag='1'),timeout=10)
    except:
        return False
    else:
        res=re.findall('szJcpResult="(.*?)"',r.text)[0].split('[Success]')[1].split(';')
        return int(res[2].split('=')[1])

def get_server_port(ip):
    sk=socket.socket(socket.AF_INET,socket.SOCK_STREAM,0)
    try:
        sk.connect((ip,9999))
    except:
        pass
    else:
        sk.send(b'portcfg -act list')
        recv_str=sk.recv(4096).decode()
        sk.close()
        res=recv_str.split('[Success]')[1].split(';')
        data={}
        for i in res:
            if i == "\r\n\r\n":
                pass
            else:
                data[i.split('=')[0]]=i.split('=')[1]
        return data

def get_img_from_rtsp(ip,img_name,stream_type,path,port='554'): # 从rtsp取流抓图
    try:
        cap = VideoCapture("rtsp://"+ip+':'+port+"/"+stream_type)
    except:
        print('RTSP ERROR')
    else:
        ret,img = cap.read()
        if ret:
            imwrite(path+img_name+'.jpg',img)
            cap.release()
            return True
        return False

def is_update(ip):  # 升级状态
    r = get_upgrade_progress(ip)
    print('{}%'.format(r),end="\r")
    if r==100:
        return True;
    elif r>=0 and r<100:
        sleep(2)
        return is_update(ip)
    else:
        return False

def get_upgrade_file(dirname):  # 获取升级文件
    lists=[]
    for filename in os.listdir(dirname):
        lists.append(dirname+'/'+filename)
    if len(lists)==0:
        print('升级包为空')
    return lists

def get_version(ip):    # 获取设备版本
    try:
        r=requests.get('http://'+ip+'/?jcpcmd=version -act list',cookies=dict(loginflag='1'),timeout=3)
    except:
        return False
    else:
        res=re.findall('szJcpResult="(.*?)"',r.text)[0].split('[Success]')[1].split(';')
        return res[4].split('=')[1]

def wait_untile_upgrade_success(ip):    # sleep直到设备启动
    index=1
    while True:
        if get_version(ip):
            break
        else:
            print('.'*index,end="\r")
            index+=1
            sleep(5)
    print('')



def set_osd(ip, osd):    # 设置osd为版本号
    url='http://'+ip+'/?jcpcmd=osdcfg -act set  -nameen 1 -nameleft 1498 -nametop 1047 -name "{}"'.format(osd)
    r=requests.get(url,cookies=dict(loginflag='1'), timeout=2)

def set_ircut_mode(ip, model):   # 设置ircut

    if model == '1':  # 光敏50
        url = 'http://'+ip+'/?jcpcmd=ircfg -act set -irswitchmode 1 -turnonlux 0 -webturnonlux 50'
        
    elif model == '2':    # 光敏100
        url = 'http://'+ip+'/?jcpcmd=ircfg -act set -irswitchmode 1 -turnonlux 0 -webturnonlux 100'
        
    elif model == '3':    # 光敏1
        url = 'http://'+ip+'/?jcpcmd=ircfg -act set -irswitchmode 1 -turnonlux 0 -webturnonlux 1'
        
    elif model == '4':    # 软光敏1
        url = 'http://'+ip+'/?jcpcmd=lightcfg -act set -openlightlux 1'
        
    elif model == '5':    # 软光敏100
        url = 'http://'+ip+'/?jcpcmd=lightcfg -act set -openlightlux 100'
        
    elif model == '6':    # 软光敏50
        url = 'http://'+ip+'/?jcpcmd=lightcfg -act set -openlightlux 50'
        
    try:
        r = requests.get(url, cookies=dict(loginflag='1'), timeout=1)
    except:
        return False
    else:
        return True


if __name__ == '__main__':
    ip = input('请输入IP地址:')
    # sleep_time = input('休息间隔:')
    sleep_time = ''
    if sleep_time == '':
        sleep_time = 0
    else:
        sleep_time = int(sleep_time)
    res = re.match('(?:\d+\.){3}\d+$', ip)
    if res==None:
        raise Exception('地址格式错误')
    update_file_dir = input('请输入升级包文件夹(不输入表示文件夹为upgrade_file):')
    # update_file_dir = ''
    if update_file_dir == '':
        files = get_upgrade_file('upgrade_file')
    else:
        files = get_upgrade_file(update_file_dir)
    mkdir(ip)
    now_time=strftime('%Y-%m-%d_%H-%M-%S')
    mkdir(ip+'/'+now_time)
    path=ip+'/'+now_time+'/'
    index=1
    for file in files:
        print("NO.{}---file is {}".format(index,file))
        index+=1
        upgrade(ip,file)    #上传升级包
        if is_update(ip):   #正常升级
            print('Please wait for the upgrade to complete')
            sleep(30)
            wait_untile_upgrade_success(ip) #等待设备完成升级
            check_video_size(ip)    #检查分辨率是否最大
            version = get_version(ip) #获取版本
            print("version is {}".format(version))
            set_osd(ip, version) #设置osd
            sleep(5)
            if sleep_time:
                sleep(sleep_time)
            
            if get_device_type(ip) == '1':  #红外版本
                set_ircut_mode(ip, '2')  #黑白
                sleep(15)
                if get_img_from_rtsp(ip,'M_GRAY_'+version,'stream1',path):  #获取主码流
                    print("save Master Gray image success")
                if get_img_from_rtsp(ip,'S_GRAY_'+version,'stream2',path):  #获取子码流
                    print("save Slave Gray image success")
                set_ircut_mode(ip, '3')  #彩色
                sleep(15)
                if get_img_from_rtsp(ip,'M_COLOR_'+version,'stream1',path): #获取主码流
                    print("save Master Color image success")
                if get_img_from_rtsp(ip,'S_COLOR__'+version,'stream2',path):    #获取子码流
                    print("save Slave Color image success")
                set_ircut_mode(ip, '1')  #光敏

            elif get_device_type(ip) == '2':    #黑光版本
                sleep(10)
                if get_img_from_rtsp(ip,'M_'+version,'stream1',path):   #获取主码流
                    print("save Master image success")
                if get_img_from_rtsp(ip,'S_'+version,'stream2',path):   #获取子码流
                    print("save Slave image success")
            
            elif get_device_type(ip) == '3':    #软光敏版本
                print('软光敏版本')
                set_ircut_mode(ip, '5')  #软光敏-黑白
                sleep(15)
                if get_img_from_rtsp(ip,'M_GRAY_'+version,'stream1',path):  #获取主码流
                    print("save Master Gray image success")
                if get_img_from_rtsp(ip,'S_GRAY_'+version,'stream2',path):  #获取子码流
                    print("save Slave Gray image success")
                set_ircut_mode(ip, '4')  #软光敏-彩色
                sleep(15)
                if get_img_from_rtsp(ip,'M_COLOR_'+version,'stream1',path): #获取主码流
                    print("save Master Color image success")
                if get_img_from_rtsp(ip,'S_COLOR__'+version,'stream2',path):    #获取子码流
                    print("save Slave Color image success")
                set_ircut_mode(ip, '6')  #软光敏-自动50
            
                
            video_info_m, video_info_s = get_video_info(ip, '80')
            # 主码流录像
            if video_info_m['codec'] == '2':    #avc
                a = AvcRecoder(path+version+'.mp4', ip, port=554, video_recode_time=20, stream_type=1)
            else:
                a = HevcRecoder(path+version+'.mp4', ip, port=554, video_recode_time=20, stream_type=1)
            a.main()
            
            # 从码流录像
            if video_info_s['codec'] == '2':    #avc
                a = AvcRecoder(path+version+'_slave.mp4', ip, port=554, video_recode_time=20, stream_type=2)
            else:
                a = HevcRecoder(path+version+'_slave.mp4', ip, port=554, video_recode_time=20, stream_type=2)
            a.main()
        else:
            print('upgrade error!')
