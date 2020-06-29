from threading import Thread,Lock
#from multiprocessing import Process.thread
def a():
    global n
    for i in range(10):
        n+=1
        #n-=1
    
n=0
threads=[]
for i in range(4):
    thread=Thread(target=a)
    threads.append(thread)

for thread in threads:
    thread.start()

for thread in threads:
    thread.join()

print(n)
