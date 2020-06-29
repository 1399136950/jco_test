import socket

def build_connect(addr):
    s = socket.socket()
    s.settimeout(10)
    s.connect(addr)
    return s


addr = ('192.168.201.201', 80)

s = build_connect(addr)

s.send(b'GET HTTP\1.1\r\nHost:192.168.201.201\r\n\r\n')
