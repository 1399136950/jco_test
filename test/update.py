import requests
from time import sleep

file = '8.28-VB-SSC325.starlight.HDXGP2P.gen.zh.201908281.IPC2.H(F)39_H(F)29_IMX335_H(F)36_SC3235_SC4236.tgz'
with open(file,'rb') as fd:
    content = fd.read()
url = 'http://192.168.150.55/webs/updateCfg'
data={'filepath':(file,content)}

for i in range(10):
    try:
        r=requests.post(url,files=data)
    except:
        sleep(30)
    else:
        print('HTTP_STATUS',r.status_code)
        sleep(90)
