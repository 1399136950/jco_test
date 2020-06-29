import requests
from threading import Thread
import math
from time import time
import sys


def analysis_url(url):
    file_name = url.split('/')[-1]
    return file_name


def main(url):
    file_name = analysis_url(url)
    with open(file_name, 'w+') as fd:
        pass
    r = requests.head(url)
    thread_num=4
    size = int(r.headers['Content-Length'])

    avg_size = math.ceil(size/thread_num)
    t=[]
    for i in range(thread_num):
        start = i*avg_size
        if start >= size -1:
            break
        end = ((i+1)*avg_size)-1
        if end > (size - 1):
            end = size - 1
        t.append(Thread(target=down, args=(url, file_name, start, end)))
    for i in t:
        i.start()
    for i in t:
        i.join()


def down(url, file_name, start, end):
    headers = {}
    headers['Range'] = 'bytes={}-{}'.format(start, end)
    r = requests.get(url, headers=headers)
    r.close()
    with open(file_name, 'ab+') as fd:
        fd.seek(start)
        fd.write(r.content)
    

if __name__ == '__main__':
    url = sys.argv[1]
    s=time()
    main(url)
    e=time()
    print(e-s)
