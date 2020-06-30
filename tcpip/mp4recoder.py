from mp4struct import Mp4Struct, H264SpsStruct, H265SpsStruct, H265_Nal_Unit
# from threading import Thread
import socket
import time
import re
import os
import struct
import select
import wave
import base64
import hashlib


class AvcRecoder(Mp4Struct):


    def __init__(self, filename, ip, port=554, stream_type=1, video_recode_time=5, encode_type='avc'):
        super().__init__(filename, encode_type)
        self.ip = ip
        self.port = port
        self.stream_type = stream_type
        self.video_recode_time = video_recode_time*90000
        self.heartbeat_time = 30 # RTSP心跳间隔
        self.record_status = False
        self.log_path = 'log/'+ip + '.log'
        self.types = [
            '没有定义',
            '非IDR',
            '片分区A',
            '片分区B',
            '片分区C',
            'IDR',
            'SEI',
            'SPS',
            'PPS',
            '序列结束',
            '序列结束',
            '码流借宿',
            '填充'
        ]
        
    def send_data(self, sock, data):
        sock.send(data)
        rtv = sock.recv(4096)
        return rtv
        
    def send_heart_beat_pack(self, sock, session, cseq):
        data = 'ANNOUNCE rtsp://{}:{}/stream{} RTSP/1.0\r\nCSeq: {}\r\nSession: {}\r\nUser-Agent: Jabsco NVS\r\n\r\n'.format(self.ip, self.port, self.stream_type, cseq, session).encode()
        sock.send(data)
        
    def unpack_rtsp(self, s):
        buff = b''
        while True:
            data = s.recv(1)
            buff += data
            if data == '\n'.encode():
                if buff[-4:] == b'\r\n\r\n':
                    break
        buff += s.recv(8)
        with open(self.log_path,'a+') as fd:
            buff = re.sub('\r\n',';',buff.decode())
            fd.write('[RTSP]RTSP' + buff + '\r\n')
        return buff
    
    def get_md5_response(self, user,passwd,realm,nonce,uri,public_method):
        a1=hashlib.md5()
        a2=hashlib.md5()
        a3=hashlib.md5()
        str1='{}:{}:{}'.format(user,realm,passwd).encode()
        a1.update(str1)
        str1=a1.hexdigest()
        str2='{}:{}'.format(public_method,uri).encode()
        a2.update(str2)
        str2=a2.hexdigest()
        str3='{}:{}:{}'.format(str1,nonce,str2).encode()
        a3.update(str3)
        str3=a3.hexdigest()
        return str3
    
    def describe_method(self, s, ip, port, stream_type):
        print('describe_method')
        while True:
            url = 'DESCRIBE rtsp://{}:{}/stream{} RTSP/1.0\r\nCSeq: {}\r\nAccept: application/sdp\r\nUser-Agent: Jabsco NVS\r\n\r\n'.format(ip, port, stream_type, self.cseq).encode()
            if self.username != None:
                if self.encryption_method == 'Basic':
                    user_passwd = base64.b64encode('{}:{}'.format(self.username, self.password).encode()).decode()
                    url = 'DESCRIBE rtsp://{}:554/stream{} RTSP/1.0\r\nCSeq: {}\r\nAuthorization: Basic {}\r\nAccept: application/sdp\r\nUser-Agent: Jabsco NVS\r\n\r\n'.format(ip, stream_type, self.cseq, user_passwd).encode()
                elif self.encryption_method == 'Digest':
                    public_method = url.decode().split(' ')[0]
                    uri = url.decode().split(' ')[1]
                    response = self.get_md5_response(self.username, self.password, realm, nonce, uri, public_method)
                    url = 'DESCRIBE rtsp://{}:{}/stream{} RTSP/1.0\r\nCSeq: {}\r\nAuthorization: {} username="{}", realm="{}", nonce="{}", uri="{}", response="{}"\r\nAccept: application/sdp\r\nUser-Agent: Jabsco NVS\r\n\r\n'.format(ip, port, stream_type, self.cseq, self.encryption_method, self.username, realm, nonce, uri, response).encode()
            rtv = self.send_data(s, url)
            self.cseq += 1
            print(url.decode())
            print(rtv.decode())
            if rtv.decode().split('\r\n')[0] != 'RTSP/1.0 200 OK':
                if rtv.decode().split('\r\n')[0] == 'RTSP/1.0 401 Unauthorized':
                    arr = rtv.decode().split('\r\n')
                    for i in arr:
                        if re.match('^WWW-Authenticate.*?', i):
                            self.encryption_method = re.findall('^WWW-Authenticate: (\w+) .*?$', i)[0]
                            print(self.encryption_method)
                            if self.encryption_method == 'Digest':
                                realm = re.findall('realm="(.*?)"', i)[0]
                                nonce = re.findall('nonce="(.*?)"', i)[0]
                            elif self.encryption_method == 'Basic':
                                realm = re.findall('realm="(.*?)"', i)[0]
                    self.username = input('请输入用户名 : ')
                    self.password = input('请输入密码   : ')
                else:
                    return False,rtv.decode().split('\r\n')[0]
            else:
                self.sdp_info = self.analysis_sdp_info(rtv.decode())
                break
        return True, ''
        
    def setup_method_video(self, s, ip, port, stream_type):
        url = 'SETUP rtsp://{}:{}/stream{}/trackID=1 RTSP/1.0\r\nCSeq: {}\r\nTransport: RTP/AVP/TCP;unicast;interleaved=0-1\r\nUser-Agent: Jabsco NVS \r\n\r\n'.format(ip, port, stream_type, self.cseq).encode()
        rtv = self.send_data(s, url)
        self.cseq += 1
        print(url.decode())
        print(rtv.decode())
        if rtv.decode().split('\r\n')[0] != 'RTSP/1.0 200 OK':
            return False, rtv.decode().split('\r\n')[0]
        else:
            arr = rtv.decode().split('\r\n')
            for i in arr:
                if re.findall('^Session:(.*?)', i):
                    self.session = re.sub(' ', '', re.findall('^Session:(.*?)$', i)[0].strip())
        return True, ''
    
    def setup_method_audio(self, s, ip, port, stream_type):
        url = 'SETUP rtsp://{}:{}/stream{}/trackID=2 RTSP/1.0\r\nCSeq: {}\r\nSession: {}\r\nTransport: RTP/AVP/TCP;unicast;interleaved=2-3\r\nUser-Agent: Jabsco NVS \r\n\r\n'.format(ip, port, stream_type, self.cseq, self.session).encode()   # 音频数据请求
        rtv = self.send_data(s, url)
        self.cseq += 1
        print(url.decode())
        print(rtv.decode())
        if rtv.decode().split('\r\n')[0] != 'RTSP/1.0 200 OK':
            pass
        else:
            print('初始化audio参数')
            self.init_audio_parameter() # 初始化音频相关数据
        return True, ''
    
    def play_method(self, s, ip, port, stream_type):
        url = 'PLAY rtsp://{}:{}/stream{}/ RTSP/1.0\r\nCSeq: {}\r\nSession:  {}\r\nRange: npt=0.000-\r\n\r\n'.format(ip, port, stream_type, self.cseq, self.session).encode()
        rtv = self.send_data(s, url)
        self.cseq += 1
        print(url.decode())
        print(rtv.decode())
        if rtv.decode().split('\r\n')[0] != 'RTSP/1.0 200 OK':
            return False,rtv.decode().split('\r\n')[0]
        else:
            self.start_timestamp = int(re.findall('rtptime=(\d+)',rtv.decode())[0])
            print(self.start_timestamp)
        return True, ''
    
    def async_device_time(self, s):
        url =  'CMD * RTSP/1.0\r\nCSeq: {}\r\nAccept:TEXT/JCP\r\nContent-Length:47\r\n\r\ntimecfg -act poweron_sync   -time {} \r\n'.format(self.cseq, str(time.time()).split('.')[0]).encode()
        a='timecfg -act poweron_sync   -time {} \r\n'.format(str(time.time()).split('.')[0])
        # print(len(a))
        rtv = self.send_data(s, url)
        self.cseq += 1
        print(url.decode())
        print(rtv.decode())
        return rtv
    
    def connect_rtsp(self, s, ip, port, stream_type=2):
        
        self.username, self.password = None, None
        self.cseq = 1
        # self.async_device_time(s)
        r1, msg1 = self.describe_method(s, ip, port, stream_type)
        if r1:
            r2, msg2 = self.setup_method_video(s, ip, port, stream_type)
            if r2:
                r3, msg3 = self.setup_method_audio(s, ip, port, stream_type)
                if r3:
                    r4, msg4 = self.play_method(s, ip, port, stream_type)
                    if r4:
                        # self.async_device_time(s)
                        return True, ''
                    else:
                        return False, msg4
                else:
                    return False, msg3
            else:
                return False, msg2
        else:
            return False, msg1
            
    def analysis_sdp_info(self, sdp_info):
        info={}
        arr = sdp_info.split('\r\n')
        for i in arr:
            if re.match('^a=frame.*?',i):
                key = i.split('=')[1].split(':')[0]
                val = i.split('=')[1].split(':')[1]
                info[key] = val
            if re.match('^a=x-framerate.*?',i):
                key = i.split('=')[1].split(':')[0]
                val = i.split('=')[1].split(':')[1]
                info[key] = val
            if re.match('^a=Media_header.*?',i):
                t = re.findall('^a=Media_header:(.*?)$', i)[0]
                key = t.split('=')[0]
                val = t.split('=')[1]
                info[key] = val
            if re.match('^a=rtpmap.*?',i):
                print(i)
            if re.match('^a=fmtp.*?',i):
                arr = i.split(' ')[1].split(';')
                for t in arr:
                    key = t.split('=')[0]
                    val = re.findall('.*?=(.*?)$',t)[0]
                    info[key] = val
        print(info)
        return info
    
    def ayanysls_sps(self, sps):
        pass
    
    def main(self):
        self.record_status = True
        s = socket.socket()
        s.connect((self.ip, self.port))
        rtv, msg = self.connect_rtsp(s, self.ip, self.port, self.stream_type)
        if rtv:
            print('连接RTSP成功')
        else:
            print('err', msg)
            exit(0)
        start = time.time()
        p_count = 0
        frame = []
        frame_size = 0
        frame_num = 1
        audio_num = 0
        video_chunk_num = 1
        audio_chunk_num = 1
        format_1 = struct.Struct('B')
        format_2 = struct.Struct('>H')
        format_3 = struct.Struct('3B')
        format_4 = struct.Struct('>I')
        offset = self.offset + 8
        timestamp = self.start_timestamp
        sample_delta_count = 0
        audio_type = None
        try:
            avc_frame_time = int(90000/int(self.sdp_info['framerate']))
        except:
            avc_frame_time = 3000
        while sample_delta_count < self.video_recode_time:
            if time.time() - start > self.heartbeat_time:
                self.send_heart_beat_pack(s, self.session, self.cseq)
                self.cseq += 1
                start = time.time()
            rtsp_head = s.recv(4)
            while len(rtsp_head) < 4:
                print('rtsp_head', len(rtsp_head))
                rtsp_head += s.recv(4 - len(rtsp_head))
            if rtsp_head == b'RTSP':
                print('RTSP'+self.unpack_rtsp(s))
                continue
            elif rtsp_head == b'':
                print('empty data')
                break
            rtp_data_len = (rtsp_head[2] << 8) + rtsp_head[3]
            rtsp_data = s.recv(rtp_data_len)
            while len(rtsp_data) < rtp_data_len:
                rtsp_data += s.recv(rtp_data_len - len(rtsp_data))
            if rtsp_head[1] == 0x63:
                print(rtsp_data)
                with open(self.log_path, 'ab+') as fda:
                    fda.write('[ALARM]'.encode() + rtsp_data+'\r\n'.encode())
                continue
            rtp_head = rtsp_data[0:12]
            seq = (rtp_head[2] << 8) + rtp_head[3]
            
            PT_TYPE = rtp_head[1] & 0x7f
            if PT_TYPE == 96:
                rtp_idn = rtsp_data[12]
                nal_type = (rtp_idn & 0x1f)
                if nal_type >= 24 :
                    rtp_head_t = rtsp_data[13]
                    rtp_head_type = rtp_head_t & 0x1f
                    S = rtp_head_t >> 7
                    E = (rtp_head_t >> 6) & 0x1
                    if S == 1:
                        frame = []
                        frame_size = 0
                        if rtp_head_type == 7 or rtp_head_type == 8:
                            sample_delta = 1
                            timestamp = format_4.unpack(rtp_head[4:8])[0]
                            self.add_video_stts_element(sample_delta)
                        else:
                            now_timestamp = format_4.unpack(rtp_head[4:8])[0]
                            sample_delta = now_timestamp - timestamp
                            if sample_delta <= 0 or sample_delta > 0xffffffff:
                                sample_delta = avc_frame_time
                            self.add_video_stts_element(sample_delta)
                            timestamp = now_timestamp
                        frame_tmp = struct.pack('>B', (rtsp_data[12] & 0xe0)+(rtsp_data[13] & 0x1f)) + rtsp_data[14:]
                        frame.append(frame_tmp)
                        frame_size += len(frame_tmp)
                        
                    else:
                        frame.append(rtsp_data[14:])
                        frame_size += len(rtsp_data[14:])
                        if E == 1:
                            if rtp_head_type == 5 or rtp_head_type == 7 or rtp_head_type == 8:
                                self.add_video_stss_element(frame_num)
                            frame_head = b'\x60' + format_3.pack((frame_size+4)>>16, ((frame_size+4)&0xffff)>>8, (frame_size+4)&0xff) + b'\x01\x00\x00\x00' + format_4.pack(frame_size)
                            self.add_mdat_element(frame_head+b''.join(frame))
                            self.add_video_stsz_element(frame_size+4)
                            self.add_video_stsc_element(video_chunk_num)
                            self.add_video_stco_element(offset+8)
                            frame_num += 1
                            video_chunk_num += 1
                            offset += (frame_size+12)
                            pre_type = rtp_head_type
                            sample_delta_count +=  sample_delta
                else:
                    frame = rtsp_data[12:]
                    frame_size = len(frame)
                    
                    if nal_type == 7 or nal_type == 8:
                        sample_delta = 1
                        timestamp = format_4.unpack(rtp_head[4:8])[0]
                        self.add_video_stts_element(sample_delta)
                    else:
                        now_timestamp = format_4.unpack(rtp_head[4:8])[0]
                        sample_delta = now_timestamp - timestamp
                        if sample_delta <= 0 or sample_delta > 0xffffffff:
                            sample_delta = avc_frame_time
                        self.add_video_stts_element(sample_delta)
                        timestamp = now_timestamp
                    
                    if nal_type in [5, 7, 8]:
                        self.add_video_stss_element(frame_num)
                        if nal_type == 8:
                            pps = frame
                        elif nal_type == 7:
                            sps = frame
  
                    frame_head = b'\x60' + format_1.pack((frame_size+4) >> 16) + format_1.pack((frame_size+4) >> 8) + format_1.pack((frame_size+4) & 0xff) + b'\x01\x00\x00\x00' + format_4.pack(frame_size)
                    self.add_mdat_element(frame_head+frame)
                    self.add_video_stsz_element(frame_size+4)
                    self.add_video_stsc_element(video_chunk_num)
                    self.add_video_stco_element(offset+8)
                    frame_num += 1
                    video_chunk_num += 1
                    offset += (frame_size+12)
                    pre_type = nal_type
                    sample_delta_count +=   sample_delta
                    
            elif PT_TYPE == 0 or PT_TYPE == 8:# ulaw
                audio_type = PT_TYPE
                audio_data = rtsp_data[12:]
                trak_id = b'\x61'
                data_len = len(audio_data)
                data_len_hex = format_1.pack(data_len >> 16) + format_2.pack(data_len & 0xffff)
                audio_head = trak_id + data_len_hex + b'\x01' + data_len_hex
                self.add_mdat_element(audio_head+audio_data) # 添加音频数据
                self.add_audio_stsz_element(data_len)
                self.add_audio_stts_element(800)
                self.add_audio_stco_element(offset+8)
                self.add_audio_stsc_element(audio_chunk_num)
                audio_num += 1
                audio_chunk_num += 1
                offset += (data_len + len(audio_head))
            else:
                print('长度:{}\tPT_TYPE:{}\t{}\tseq:{}'.format(rtp_data_len, PT_TYPE, 'unknow type', seq))
        
        print('stop record')
        s.close()
        profile_level_id = self.sdp_info['profile-level-id']
        self.set_profile_level_id(profile_level_id)
        self.set_sps(sps)
        self.set_pps(pps)
        print('sps', sps)
        sps_struct = H264SpsStruct(sps)
        width, height = sps_struct.width, sps_struct.height
        print(width, height)
        self.set_width(width)
        self.set_hight(height)
        if audio_type != None:
            self.set_audio_type(audio_type)
        s=time.time()
        self.close()
        e=time.time()
        print('cost', e-s)



class HevcRecoder(AvcRecoder):
    
    
    def __init__(self, filename, ip, port=554, stream_type=1, video_recode_time=5, encode_type='hevc'):
        super().__init__(filename, ip, port=port, stream_type=stream_type, video_recode_time=video_recode_time, encode_type=encode_type)
        
    def main(self):
        self.record_status = True
        s = socket.socket()
        s.connect((self.ip, self.port))
        rtv, msg = self.connect_rtsp(s, self.ip, self.port, self.stream_type)
        if rtv:
            print('连接RTSP成功')
        else:
            print(msg)
            exit(0)
        start = time.time()
        p_count = 0
        frame = []
        frame_size = 0
        frame_num = 1
        audio_num = 0
        video_chunk_num = 1
        audio_chunk_num = 1
        format_1 = struct.Struct('B')
        format_2 = struct.Struct('>H')
        format_3 = struct.Struct('3B')
        format_4 = struct.Struct('>I')
        offset = self.offset + 8 # 预留八个字节给mdat首部，4字节长度，4字节类型
        timestamp = self.start_timestamp
        sample_delta_count = 0
        audio_type = None
        try:
            avc_frame_time = int(90000/int(self.sdp_info['framerate']))
        except:
            avc_frame_time = int(90000/int(self.sdp_info['x-framerate']))
            
        while sample_delta_count < self.video_recode_time:
            if time.time() - start > self.heartbeat_time:
                self.send_heart_beat_pack(s, self.session, self.cseq)
                self.cseq += 1
                start = time.time()
            rtsp_head = s.recv(4)
            while len(rtsp_head) < 4:
                print('rtsp_head', len(rtsp_head))
                rtsp_head += s.recv(4 - len(rtsp_head))
            if rtsp_head == b'RTSP':
                print('RTSP'+self.unpack_rtsp(s))
                continue
            elif rtsp_head == b'':
                print('empty data')
                break
            rtp_data_len = (rtsp_head[2] << 8) + rtsp_head[3]
            rtsp_data = s.recv(rtp_data_len)
            while len(rtsp_data) < rtp_data_len:
                rtsp_data += s.recv(rtp_data_len - len(rtsp_data))
            if rtsp_head[1] == 0x63:
                print(rtsp_data)
                with open(self.log_path, 'ab+') as fda:
                    fda.write('[ALARM]'.encode() + rtsp_data+'\r\n'.encode())
                continue
            rtp_head = rtsp_data[0:12]
            seq = (rtp_head[2] << 8) + rtp_head[3]
            
            PT_TYPE = rtp_head[1] & 0x7f
            if PT_TYPE == 96:   # 视频数据
                rtp_idn = rtsp_data[12]
                nal_type = (rtp_idn  >> 1) & 0x3f
                if nal_type == 49:  # 分片nal
                    rtp_head_t = rtsp_data[14]
                    rtp_head_type = rtp_head_t & 0x3f
                    S = rtp_head_t >> 7
                    E = (rtp_head_t >> 6) & 0x1

                    if S == 1:
                        frame = []
                        frame_size = 0
                        if rtp_head_type in [32, 33, 34]:
                            sample_delta = 1
                            timestamp = format_4.unpack(rtp_head[4:8])[0]
                            self.add_video_stts_element(sample_delta)
                        else:
                            now_timestamp = format_4.unpack(rtp_head[4:8])[0]
                            # print(now_timestamp,rtp_head_type)
                            sample_delta = now_timestamp - timestamp
                            if sample_delta <= 0 or sample_delta > 0xffffffff:
                                sample_delta = avc_frame_time
                            self.add_video_stts_element(sample_delta)
                            timestamp = now_timestamp
                            
                        nal_head =  ((rtsp_data[12] & 0b10000000) + (rtp_head_type << 1)) + (rtsp_data[12] & 0b1)  # 重新生成nal_head
                        
                        frame_tmp = format_1.pack(nal_head) + format_1.pack(rtsp_data[13]) + rtsp_data[15:]
                        frame.append(frame_tmp)
                        frame_size += len(frame_tmp)
                        
                    else:
                        frame.append(rtsp_data[15:])
                        frame_size += len(rtsp_data[15:])
                        if E == 1:
                            if rtp_head_type in [19, 20, 32, 33, 34]:
                                self.add_video_stss_element(frame_num)
                            frame_head = b'\x60' + format_3.pack((frame_size+4)>>16, ((frame_size+4)&0xffff)>>8, (frame_size+4)&0xff) + b'\x01\x00\x00\x00' + format_4.pack(frame_size)
                            self.add_mdat_element(frame_head + b''.join(frame))
                            self.add_video_stsz_element(frame_size+4)
                            self.add_video_stsc_element(video_chunk_num)
                            self.add_video_stco_element(offset+8)
                            frame_num += 1
                            video_chunk_num += 1
                            offset += (frame_size+12)
                            pre_type = rtp_head_type
                            sample_delta_count += sample_delta
                            
                else:   # 单独nal
                    
                    frame = rtsp_data[12:]
                    frame_size = len(frame)
                    if nal_type in [32, 33, 34]:
                        # print(format_4.unpack(rtp_head[4:8])[0], nal_type)
                        sample_delta = 1
                        timestamp = format_4.unpack(rtp_head[4:8])[0]
                        self.add_video_stts_element(sample_delta)
                        if nal_type == 32:
                            vps = frame
                        elif nal_type == 33:
                            sps = frame
                        elif nal_type == 34:
                            pps = frame
                    else:
                        now_timestamp = format_4.unpack(rtp_head[4:8])[0]
                        # print(now_timestamp, nal_type)
                        sample_delta = now_timestamp - timestamp
                        if sample_delta <= 0 or sample_delta > 0xffffffff:
                            sample_delta = avc_frame_time
                        self.add_video_stts_element(sample_delta)
                        timestamp = now_timestamp
                    
                    if nal_type in [19, 20, 32, 33, 34]:
                        self.add_video_stss_element(frame_num) 
                            
                    frame_head = b'\x60' + format_1.pack((frame_size+4) >> 16) + format_1.pack((frame_size+4) >> 8) + format_1.pack((frame_size+4) & 0xff) + b'\x01\x00\x00\x00' + format_4.pack(frame_size)
                    self.add_mdat_element(frame_head+frame)
                    self.add_video_stsz_element(frame_size+4)
                    self.add_video_stsc_element(video_chunk_num)
                    self.add_video_stco_element(offset+8)
                    frame_num += 1
                    video_chunk_num += 1
                    offset += (frame_size+12)
                    pre_type = nal_type
                    sample_delta_count += sample_delta
                    
            elif PT_TYPE == 0 or PT_TYPE == 8:  # 音频数据
                audio_type = PT_TYPE

                audio_data = rtsp_data[12:]
                trak_id = b'\x61'
                data_len = len(audio_data)
                data_len_hex = format_1.pack(data_len >> 16) + format_2.pack(data_len & 0xffff)
                audio_head = trak_id + data_len_hex + b'\x01' + data_len_hex
                self.add_mdat_element(audio_head+audio_data) # 添加音频数据
                self.add_audio_stsz_element(data_len)
                self.add_audio_stts_element(800)
                self.add_audio_stco_element(offset+8)
                self.add_audio_stsc_element(audio_chunk_num)
                audio_num += 1
                audio_chunk_num += 1
                offset += (data_len + len(audio_head))
            else:
                print('长度:{}\tPT_TYPE:{}\t{}\tseq:{}'.format(rtp_data_len, PT_TYPE, 'unknow type', seq))
        
        print('stop record')
        s.close()
        
        # sps = base64.b64decode(self.sdp_info['sprop-sps'])
        # pps = base64.b64decode(self.sdp_info['sprop-pps'])
        # vps = base64.b64decode(self.sdp_info['sprop-vps'])
        
        self.set_sps(sps)
        self.set_pps(pps)
        self.set_vps(vps)
        
        '''从sps中解析出分辨率大小'''
        sps_rbsp_byte = H265_Nal_Unit(sps).rbsp_byte
        print(sps_rbsp_byte)
        sps_struct = H265SpsStruct(sps_rbsp_byte)
        width, height = sps_struct.get_width_height()
        print(width, height)
        
        self.set_width(width)
        self.set_hight(height)
        
        if audio_type != None:  # 设置音频编码类型 ulaw or alaw
            self.set_audio_type(audio_type)
            
        s = time.time()
        self.close()
        e = time.time()
        print('cost', e-s)
