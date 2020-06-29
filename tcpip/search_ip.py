import socket
import struct


def get_queries(domain, search_type, search_class):
    fmt = struct.Struct('H')
    res = [ str(len(i))+i for i in domain.split('.') ]
    r = ''.join(res) + '0'
    return r.encode() + fmt.pack(search_type) + fmt.pack(search_type)
    
if __name__ == '__main__':
    s  = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.SOL_UDP)
    data = b'1231230'
    s.sendto(data,('192.168.222.188',53))

