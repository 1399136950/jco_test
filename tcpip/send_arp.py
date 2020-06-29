import socket
import struct


s = socket.socket(socket.PF_PACKET, socket.SOCK_RAW, socket.htons(0x0806))

dst_mac =
src_ip =



