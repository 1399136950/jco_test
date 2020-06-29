import socket
import struct
import time


def get_checksum(data):
    count = 0
    sum = 0

    while count + 2 < len(data):
        sum += ((data[count+1] << 8) + data[count])
        count += 2

    if count < len(data):
        sum += ((0 << 8) + data[count])

    sum = (sum >> 16) + (sum & 0xffff)

    ans = (~sum) & 0xffff

    return ans



icmp_head = struct.pack('BBHHH', 8, 0, 0, 10000, 0)

data = bytes('hello world'.encode())

pack = icmp_head + data

check_num = get_checksum(pack)


icmp_head = struct.pack('BBHHH', 8, 0, check_num, 10000, 0)

pack = icmp_head + data

s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname('icmp'))

dst_ip = '192.168.0.178'

ip = socket.gethostbyname(dst_ip)

s.sendto(pack,(ip, 0))
