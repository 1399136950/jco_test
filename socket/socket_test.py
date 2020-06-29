import socket
import threading
from queue import Queue
from time import sleep

status=True
def echo_client(q,name):
    global status
    while status:
        sock, client_addr = q.get()
        print('thread {} Got connection from '.format(name), client_addr)
        buf=sock.recv(65535)
        if buf ==b'exit\n':
            status=False
            sock.close()
            break
        print(buf)
        sock.send(b'hello world')
        sleep(20)
        sock.close()
    print('thread exit')

def echo_server(networks):
    global status
    q=Queue()
    for n in range(networks):
        t=threading.Thread(target=echo_client,args=(q,n))
        t.daemon=True
        t.start()
        
    
    s=socket.socket()
    s.bind(('192.168.0.101',12254))
    s.listen(5)
    while status:
        client_sock, client_addr = s.accept()
        q.put((client_sock, client_addr))
    print('main exit')
echo_server(1)
