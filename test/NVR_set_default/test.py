import socket
from time import sleep


dafault_ip = '192.168.1.218'

index = 1

raw_data = b'do_factory_def -cmd 64'

while True:

    s = socket.socket()

    try:
        s.connect((dafault_ip, 9999))

    except:

        print('[Error]')

    else:

        s.send(raw_data)

        s.close()

        print('NO.{} [Success]'.format(index))
        
        index += 1
        
    sleep(120)
