import socket
import re
import os


def get_header(s):
    headers = []
    v = b''
    while 1:
        b = s.recv(1)
        if b == b'\r':
            next_b = s.recv(1)
            if next_b == b'\n':
                next_2b = s.recv(2)
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
    rtv['http_type'] = headers[0]
    for i in range(1,len(headers)):
        key = headers[i].split(':')[0]
        val = headers[i].split(':')[1].strip()
        rtv[key] = val  
    return rtv

def analysys_requests_type(req):
    l = req.split(' ')
    data = {}
    data['requests_type'] = l[0]
    data['http_version'] = l[2]
    url_list = l[1].split('?')
    data['path'] = url_list[0]
    paras = None
    if len(url_list) > 1:
        paras = {}
        paras_list = url_list[1].split('&')
        for i in paras_list:
            key = i.split('=')[0]
            val = i.split('=')[1]
            paras[key] = val
    data['paras'] =  paras
    return data
        
def get_http_body(code, msg):
    body="HTTP/1.1 {} OK\r\ncontent-length:{}\r\nServer:python3-web\r\n\r\n{}".format(code, len(msg), msg).encode()
    return body

def get_404_body():
    head = "HTTP/1.1 404 Not Found\r\ncontent-length:143\r\nServer:python3-web\r\n\r\n".encode()
    body = "<html><head><title>404 Not Found</title></head><body><h1>Not Found</h1><p>The requested URL was not found on this server.</p><hr></body></html>".encode()
    return head+body

s = socket.socket()

s.bind(('192.168.222.101', 8080))
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.listen(5)

while 1:
    so,h = s.accept()
    head = get_header(so)
    for i in head:
        print(i,':',head[i])
    data = analysys_requests_type(head['http_type'])
    print(data)
    request_path = data['path'][1:]
    if not os.path.exists(request_path):
        so.send(get_404_body())
        so.close()
        print('')
    else:    
        try:
            print(head['Content-Type'])
        except:
            pass
        else:
            leng = int(head['Content-Length'])
            conetnt = b''
            while leng > 0:
                if leng <= 1024:
                    buff = so.recv(leng)
                    leng = 0
                else:
                    buff = so.recv(1024)
                    leng -= 1024
                conetnt += buff
            print(len(conetnt))
            if len(conetnt) < 10000:
                print(conetnt)
        finally:
            file_type = request_path.split('.')[-1]
            
            if file_type == 'py':
            
                msg = os.popen('python {}'.format(request_path)).read()
            elif file_type == 'php':
                msg = os.popen('php {}'.format(request_path)).read()
            else:
                with open(request_path, encoding='utf-8') as fd:
                    msg = fd.read()
            so.send(get_http_body(200, msg))
            so.close()
            print('')
