import time

now_time = lambda: time.strftime('%Y-%m-%d %H:%M:%S')

while True:
    print(now_time(), end='\r')
    time.sleep(1)
