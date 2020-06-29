import requests
import time

def reboot(ip):
    url='http://'+ip+'/?jcpcmd=sysctrl -act set -cmd 0'
    try:
        r = requests.get(url, cookies=dict(loginflag='1'), timeout=10)
    except:
        return False
    else:
        return True

def snap_pic(ip):
    url = 'http://{}/cgi-bin/snap.cgi?channel=0'.format(ip)
    try:
        r = requests.get(url, timeout=10)
    except:
        return False
    else:
        if r.status_code == 200:
            if len(r.content) == 0:
                return False
            else:
                return len(r.content)
        else:
            return False




# url = 'http://192.168.1.191/cgi-bin/snap.cgi?channel=0'

video_data ={
    'action':'update',
    'group':'VENC',
    'channel':0,
    'streamType':1, # 0主码流，1从码流
    'VENC.frameRate':15,
    # 'VENC.streamMixType':1, # 碼流混合模式
    # 'VENC.h264EncLvl':0, # 編碼等級：0 - baseline profile;1 - main profile;2 - high profile
    # 'VENC.frPreeferred':1, # 是否幀率優先 1: 是, 0: 不是
    'VENC.iFrameIntv':90, # I幀間隔
    'VENC.veType':4, # 視頻編碼類型;0：H.264;4：H.265
    'VENC.bitRate':512,
    'VENC.bitRateType':0, # 碼率類型:0 - 定碼流;1 - 變碼流;2 - 按品質編碼
    # 'VENC.quality':1,
    # 'VENC.resolution':10,
    'VENC.standard':1, # 制式：0 - P制;1 - N制
    'VENC.audioInputMode':0,
    'VENC.audioInputGain':8,
    'VENC.audioOutputGain':5
}

net_data = {
   'action':'update',
   'group':'ETH',
   'ETH.no':'0',
   'ETH.dhcp':'1',
   'ETH.ipaddr':'192.168.130.184',
   'ETH.netmask':'255.255.255.128',
   'ETH.gateway':'192.168.130.138',
   'ETH.autoDns':'0',
   'ETH.dns1':'17.196.131.152',
   'ETH.dns2':'177.8.1.4' 
}

record_data = {
    'action':'list',
    'group':'RECORD',
    'channel':0,
    'beginTime':1573196458,
    'endTime':1573200058,
    'type':4294967295,
    'beginNo':0,
    'reqCount':3,
    'sessionId':0
}


ip = '192.168.130.184'

url = 'http://{}/cgi-bin/record.cgi'.format(ip)

r = requests.get(url, record_data)

res = r.text.split('\r\n')
# print(res)
[print(i) for i in res]
print(url)

'''
ip = '192.168.201.250'

while True:

    rtv = snap_pic(ip)
    if not rtv:
        break
    print(rtv)
    time.sleep(20)

    if reboot(ip):
        time.sleep(40)

'''
