from rtspclient import RtspClient
from mp4struct import Mp4Struct


url = 'rtsp://192.168.222.55/stream2'

a = RtspClient(url)

rtv,msg = a.connect()
if rtv:
    print(a.sdp_info())
    mp4fd = Mp4Struct()
