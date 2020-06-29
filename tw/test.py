import requests
import os
import re


ip = '192.168.200.179'


url = 'http://' + ip + '/cgi-bin/record.cgi?action=list&group=RECORD&channel=0&beginTime=1583857759&endTime=1583940559&type=4294967295&beginNo=0&reqCount=20&sessionId=1'

data = {
    'action':'list',
    'group':'RECORD',
    'channel':'0',
    'beginTime':'1583857759',
    'endTime':'1583940559',
    'type':'4294967295',
    'beginNo':'0',
    'reqCount':'15',
    'sessionId':'0'
}

r = requests.get(url)
r_list = r.text.split('\r\n')
[print(i) for i in r_list]

