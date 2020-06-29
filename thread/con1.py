import threading
from time import sleep

con=threading.Condition()

def a(con):
    while True:
        con.acquire()
        print('a: wait')
        con.wait()
        print('a: working now')
        con.notify()
        con.release()

def b(con):
    while True:
        sleep(3)
        print('b: let a work')
        con.acquire()
        con.notify()
        print('b: wait')
        con.wait()
       #con.release()

threads=[]
threads.append(threading.Thread(target=a,args=(con,)))
threads.append(threading.Thread(target=b,args=(con,)))
for thread in threads:
    thread.dameon=True
    thread.start()
for thread in threads:
    thread.join()
print('done')
