import serial
import time
from threading import Thread


def user_input():
    while True:
        word = input()
        ser.write(word.encode()+'\n'.encode())
        

def read_line(ser_fd):
    timestamp=time.strftime('[%Y-%m-%d %H:%M:%S]')
    res=[]
    while True:
        byt = ser.read()
        if byt == b'\x1b':
            #ser.read()
            #ser.read()
            break
        res.append(byt)
    content=timestamp+' '+(b''.join(res)).decode("utf-8", "replace")
    with open(file, 'a+', encoding='utf-8') as fd:
        fd.write(content.strip()+'\n')
    print(content.strip())
    



portx = "COM6"

file = time.strftime('%Y-%m-%d-%H_%M_%S')+'_'+portx+'.log'

bps = 115200

timex = 5

ser=serial.Serial(portx, bps, timeout=timex)

while True:
    
    read_line(ser)

