import os 
import argparse 
import socket
import struct
import select
import time


ICMP_ECHO_REQUEST = 8 # Platform specific
DEFAULT_TIMEOUT = 2
DEFAULT_COUNT = 4 


def do_checksum(source_string):
    """  Verify the packet integritity """
    sum = 0
    max_count = (len(source_string)/2)*2
    count = 0
    while count < max_count:
        val = source_string[count + 1]*256 + source_string[count]            
        sum = sum + val
        sum = sum & 0xffffffff 
        count = count + 2
    if max_count<len(source_string):
        sum = sum + ord(source_string[len(source_string) - 1])
        sum = sum & 0xffffffff 
    sum = (sum >> 16)  +  (sum & 0xffff)
    sum = sum + (sum >> 16)
    answer = ~sum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer

def send_ping(sock,  ID):
    target_addr  =  socket.gethostbyname(target_host)
    my_checksum = 0
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, my_checksum, ID, 1)# signed char,unsigned short,short
    bytes_In_double = struct.calcsize("d")
    data = (192 - bytes_In_double) * "Q"
    data = struct.pack("d", time.time()) + bytes(data.encode('utf-8'))
    # print(data)
    my_checksum = do_checksum(header + data)
    print(my_checksum)
    header = struct.pack(
        "bbHHh", ICMP_ECHO_REQUEST, 0, socket.htons(my_checksum), ID, 1
    )
    packet = header + data
    print(packet, target_addr)
    sock.sendto(packet, (target_addr, 1))
