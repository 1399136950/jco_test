import socket

def read_until(s, except_bytes):
    while 1:
        b = s.recv(1)
        

ssh_server = ('192.168.0.178', 22)
s = socket.socket()
s.connect(ssh_server)

client_protocol = b'SSH-2.0-OpenSSH_8.0\r\n'
s.send(client_protocol)
print(s.recv(100))
s.close()
