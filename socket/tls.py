import socket
import ssl
import re



def get_header(s):
    headers = []
    v = b''
    while 1:
        b = s.read(1)
        if b == b'\r':
            next_b = s.read(1)
            if next_b == b'\n':
                next_2b = s.read(2)
                headers.append(v.decode())
                v = b''
                if next_2b == b'\r\n':
                    break
                else:
                    v += next_2b
            else:
                v += b
        else:
            v += b

    rtv = {}
    rtv['status_code'] = re.findall(r'^HTTP/1\.\d (\d+) \w+$', headers[0])[0]
    for i in range(1,len(headers)):
        key = headers[i].split(':')[0]
        val = headers[i].split(':')[1].strip()
        rtv[key] = val  
    return rtv
                


hostname = 'www.baidu.com'
context = ssl.create_default_context()

sock = socket.create_connection((hostname, 443), timeout=3)
ssock = context.wrap_socket(sock, server_hostname=hostname)
print(ssock.version())
dir(ssock)

requests = 'GET / HTTP/1.1\r\nHOST:www.baidu.com\r\n\r\n'
ssock.send(requests.encode())

h=get_header(ssock)

size = int(h['Content-Length'])
content = b''
while size > 0:
    buff = ssock.read(1024)
    size -= len(buff)
    content += buff

ssock.close()
