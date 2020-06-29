import socket
import select
from time import time


def save_recv(s,data_len,timeout=3):
    fd_r_list, fd_w_list, _ = select.select([s,], [], [],timeout)
    if len(fd_r_list) == 0:
        print('timeout')
        return b''
    else:
        return fd_r_list[0].recv(data_len)

s = socket.socket()

s.connect(('192.168.233.116', 554))


cmd = 'CMD * RTSP/1.0\r\nCSeq: 1\r\nAccept:TEXT/JCP\r\nContent-Length:19\r\n\r\nversion -act list\r\n\r\n'.encode()



while True:
    s.send(cmd)

    data = save_recv(s,4096)
    if len(data) == 0:
        break
    else:
        print(data)
s.close()
