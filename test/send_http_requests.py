import requests
from time import sleep
import os
import re


def get_requests_list_from_txt(filename):
    request_lists=[]
    is_break=False
    if os.path.exists(filename):
        with open(filename,'r',encoding='utf-8') as fd:
            lines=fd.readlines()
            for line in lines:
                if line[0]=='#':
                    pass
                else:
                    tmp=line.strip('\n').split('###')
                    url=tmp[0]
                    if len(url)>0:
                        if len(url)>=3 and (url[0:3]=="'''" or url[0:3]=="'''"):
                            if is_break:
                                is_break=False
                            else:
                                is_break=True
                        if len(tmp)>1:
                            content=tmp[1]
                        else:
                            content=''
                        if is_break:
                            pass
                        else:
                            if len(url)>=3 and (url[0:3]=="'''" or url[0:3]=="'''"):
                                pass
                            else:
                                print(content)
                                request_lists.append(url)
    else:
        print("not't such file")
    print('')
    return request_lists

def send_request(url):
    res=False
    for i in range(5):
        try:
            r=requests.get(url,cookies=dict(loginflag='1'),timeout=3)
        except:
            pass
            #print('err')
        else:
            res=r.text
            break
    return res
    
first_ip=input("请输入IP:")
dev_count=input("请输入设备数量:")
if dev_count=='':
    dev_count=1
tmp=int(first_ip.split('.')[-1])

request_lists=get_requests_list_from_txt('http_requests.txt')#加载url
print(request_lists)
for i in range(int(dev_count)):
    ip=re.sub('(?P<p1>\d+)\.(?P<p2>\d+)\.(?P<p3>\d+)\.(?P<p4>\d+)', r'\1.\2.\3.'+str(int(tmp)+i), first_ip)
    print(ip)
    for request in request_lists:
        url='http://'+ip+'/?jcpcmd='+request
        res=send_request(url)
        if res:
            print(res,end='')
        else:
            print(url,'err')
        sleep(0.1)
    
