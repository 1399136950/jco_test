from multiprocessing import Process
from time import sleep


def test(n):
    sleep(n)
    print(n)

p=[]
for i in range(3):
    pro=Process(target=test,args=(5,))
    pro.start()
    
