import telnetlib
import re
from time import sleep
import requests


class MyTelnet():
    
    
    def __init__(self, ip, port=24):
        if re.match(r'^\d+.\d+.\d+.\d+$',ip):
            self.ip = ip
        else:
            raise Exception('ip err')
        if type(port) == int:
            self.port = port
        else:
            raise Exception('port err')
        try:
            self.tn = telnetlib.Telnet(self.ip, port=self.port, timeout=3)
        except:
            raise Exception('connect timeout')
        else:
            self.get_device_type()
    
    def login(self):
        _ = self.tn.read_until(b'login: ').decode()
        self.input_username()
        rtv = self.read().decode()
        # print(rtv)
        if re.match('Password|password', rtv.split('\r\n')[1]):
            # print(rtv.split('\r\n')[1])
            self.input_password()
            self.get_finished_flag()
        else:
            self.get_finished_flag()
    
    def get_device_type(self):
        url = 'http://'+self.ip+"/?jcpcmd=version -act list"
        cookies = dict(loginflag='1')
        try:
            r = requests.get(url,cookies=cookies)
        except:
            self.device_type = None
        else:
            self.device_type = re.findall('solution=(.*?);',r.text)[0]

    def input_username(self):
        self.write('root')

    def input_password(self):
        if  self.device_type == 'mstar':
            self.write("jco16888")
        if  self.device_type == 'sstar':
            self.write("jco16888")
        if  self.device_type == 'ingenic':
            self.write("jco666888")
        if  self.device_type == 'grain':
            self.write("jabsco668")
        if  self.device_type == None:
            raise Exception('device type unknow')

    def read_until(self):
        return self.tn.read_until(self.finished_flag, timeout=3)
    
    def get_result(self):
        res = self.tn.read_very_eager().decode().split('\r\n')
        return '\r\n'.join(res[1:-1])
    
    def read(self):
        r = b''
        sleep(1)
        while True:
            s = self.tn.read_eager()
            if s == b'':
                break
            r += s
        return r
    
    def exit(self):
        self.write('exit')
        self.tn.get_socket().close()
    
    def write(self, cmd, return_flag=False):
        t = cmd + '\n'
        self.tn.write(t.encode())
        if return_flag:
            return self.read_until().decode()
    
    def get_finished_flag(self):
        self.read()
        self.tn.write(b'\n')
        finished_flag = self.read()
        finished_flag = re.sub(b'\r|\n',b'',finished_flag)
        self.finished_flag = finished_flag
        print(self.finished_flag.decode())
        
class NvrTelnet(MyTelnet):

    def __init__(self, ip, port=23):
        if re.match(r'^\d+.\d+.\d+.\d+$',ip):
            self.ip = ip
        else:
            raise Exception('ip err')
        if type(port) == int:
            self.port = port
        else:
            raise Exception('port err')
        try:
            self.tn = telnetlib.Telnet(self.ip, port=self.port, timeout=3)
        except:
            raise Exception('connect timeout')

    def login(self):
        print(self.tn.read_until(b'login: ').decode())
        self.input_username()
        rtv = self.read().decode()
        if re.match('Password|password', rtv.split('\r\n')[1]):
            print(rtv.split('\r\n')[1])
            self.input_password()
            self.get_finished_flag()
        else:
            self.get_finished_flag()
            
    def input_password(self):

        self.write("jco168168")
