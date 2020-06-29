from threading import Thread
import time
from random import randint
import queue
import requests
def get_url():
        r=requests.get('https://www.baidu.com')
        #print(r.status_code)
num=600
threads=[]
now=time.time()
for i in range(num):
        thread=Thread(target=get_url)
        threads.append(thread)
for thread in threads:
        thread.start()
for thread in threads:
        thread.join()
print(time.time()-now)

now=time.time()
for i in range(num):
        pass
        #get_url()
print(time.time()-now)
		
