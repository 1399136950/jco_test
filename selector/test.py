import selectors
import socket
from urllib.parse import urlparse


class SelTest:

    def __init__(self, url):
        self.stop = False
        self.data = b''
        self.selector = selectors.DefaultSelector()
        self.s = socket.socket()
        self.s.setblocking(False)
        try:
            self.s.connect(('192.168.0.178',80))
        except BlockingIOError:
            pass
        self.selector.register(self.s.fileno(), selectors.EVENT_WRITE, self.connect)
    
    def connect(self, key, mask):
        self.selector.unregister(self.s)
        header = 'GET http://192.168.0.178/ HTTP/1.1\r\nhost:192.168.0.178\r\nConnection:close\r\n\r\n'.encode()
        self.s.send(header)
        self.selector.register(self.s.fileno(), selectors.EVENT_READ, self.readable)
        
    def readable(self, key, mask):
        d = self.s.recv(8192)
        print(len(d))
        if d:
            self.data += d
        else:
            self.selector.unregister(self.s)
            self.stop = True
            self.s.close()
            
    def loop(self):
        while not self.stop:
            event = self.selector.select()
            for key, mask in event:
                key.data(key.fileobj, mask)

if __name__ == '__main__':
    a = SelTest('')
    a.loop()

