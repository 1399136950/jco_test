# import mp4struct
import re
import socket
import time
import base64
import hashlib


class RtspClient:
    
    DEBUG = True
    
    def __init__(self, rtsp_url):
        self.heartbeat_time = 30    # 心跳间隔,定时发送心跳包
        res=re.match('^rtsp://(\d+\.\d+\.\d+\.\d+(\:\d+)?)/.*$', rtsp_url)  # 判断rtsp_url是否合法
        if res:
            self.rtsp_url = rtsp_url
            ip, port = res.groups()
            if port == None:
                self.port = 554
                self.ip = ip
            else:
                self.ip = ip.split(port)[0]
                self.port = int(port.split(':')[1])
            self.debug('IP: [{}], PORT: [{}]'.format(self.ip, self.port))
            self.log_path = 'log/'+self.ip + '.log'
        else:
            raise Exception('rtsp url error!')
            
    def send_data(self, sock, data):
        sock.send(data)
        msg = ''
        head_list = []
        while 1:
            b = sock.recv(1).decode()
            if b == '\r':
                next_1b = sock.recv(1).decode()
                if next_1b == '\n':
                    head_list.append(msg)
                    msg = ''
                    next_2b = sock.recv(2).decode()
                    if next_2b == '\r\n':
                        break
                    else:
                        msg = next_2b
            else:
                msg += b
        headers = {}
        data = None
        headers['status'] = head_list[0]
        for i in range(1, len(head_list)):
            key = head_list[i].split(':')[0]
            val = head_list[i].split(key)[1][1:].strip()
            headers[key.strip()] = val
            if key == 'Content-Length':
                data = sock.recv(int(val)).decode()
        self.debug('[send_data] [headers]: {}'.format(headers))
        self.debug('[send_data] [data]: {}'.format(data))
        return headers, data
    
    def debug(self, msg):
        if self.DEBUG:
            print(msg)
    
    def send_heart_beat_pack(self, sock, session, cseq):
        data = 'ANNOUNCE {} RTSP/1.0\r\nCSeq: {}\r\nSession: {}\r\nUser-Agent: Jabsco NVS\r\n\r\n'.format(self.rtsp_url, cseq, session).encode()
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
        a1 = hashlib.md5()
        a2 = hashlib.md5()
        a3 = hashlib.md5()
        str1 = '{}:{}:{}'.format(user,realm,passwd).encode()
        a1.update(str1)
        str1 = a1.hexdigest()
        str2 = '{}:{}'.format(public_method,uri).encode()
        a2.update(str2)
        str2 = a2.hexdigest()
        str3 = '{}:{}:{}'.format(str1,nonce,str2).encode()
        a3.update(str3)
        str3 = a3.hexdigest()
        return str3
    
    def describe_method(self, s):
        # self.debug('{0:*^100}'.format('[describe_method]'))
        while True:
            url = 'DESCRIBE {} RTSP/1.0\r\nCSeq: {}\r\nAccept: application/sdp\r\nUser-Agent: Jabsco NVS\r\n\r\n'.format(self.rtsp_url, self.cseq).encode()
            if self.username != None:
                if self.encryption_method == 'Basic':
                    user_passwd = base64.b64encode('{}:{}'.format(self.username, self.password).encode()).decode()
                    url = 'DESCRIBE {} RTSP/1.0\r\nCSeq: {}\r\nAuthorization: Basic {}\r\nAccept: application/sdp\r\nUser-Agent: Jabsco NVS\r\n\r\n'.format(self.rtsp_url, self.cseq, user_passwd).encode()
                elif self.encryption_method == 'Digest':
                    public_method = url.decode().split(' ')[0]
                    uri = self.rtsp_url
                    response = self.get_md5_response(self.username, self.password, realm, nonce, uri, public_method)
                    url = 'DESCRIBE {} RTSP/1.0\r\nCSeq: {}\r\nAuthorization: {} username="{}", realm="{}", nonce="{}", uri="{}", response="{}"\r\nAccept: application/sdp\r\nUser-Agent: Jabsco NVS\r\n\r\n'.format(self.rtsp_url, self.cseq, self.encryption_method, self.username, realm, nonce, uri, response).encode()
            self.debug('[describe_method] {}'.format(url.decode().replace('\r\n', ';')))
            headers, rtv = self.send_data(s, url)
            self.cseq += 1
            if headers['status'] != 'RTSP/1.0 200 OK':
                self.debug('[describe_method] [{}]'.format(headers['status']))
                if headers['status'] == 'RTSP/1.0 401 Unauthorized':
                    authenticate = headers['WWW-Authenticate']
                    self.encryption_method = authenticate.split(' ')[0]
                    info = authenticate.split(self.encryption_method)[1].strip()
                    realm = re.findall('realm="(.*?)"', info)[0]
                    self.debug('[describe_method] [encryption_method]: {}, [realm]: {}'.format(self.encryption_method, realm))
                    if self.encryption_method == 'Digest':
                        nonce = re.findall('nonce="(.*?)"', info)[0]
                        self.debug('[describe_method] [nonce]: {}'.format(nonce))                       
                    self.username = input('[describe_method] 请输入用户名 : ')
                    self.password = input('[describe_method] 请输入密码   : ')
                else:
                    return False, headers['status']
            else:
                self.sdp_info = self.analysis_sdp_info(rtv)
                break
        return True, headers['status']
        
    def setup_method_video(self, s, control):
        # self.debug('{0:*^100}'.format('[setup_method_video]'))
        url = 'SETUP {}/{} RTSP/1.0\r\nCSeq: {}\r\nTransport: RTP/AVP/TCP;unicast;interleaved=0-1\r\nUser-Agent: Jabsco NVS \r\n\r\n'.format(self.rtsp_url, control, self.cseq).encode()
        self.debug('[setup_method_video] {}'.format(url.decode().replace('\r\n', ';')))
        headers, rtv = self.send_data(s, url)
        self.cseq += 1
        if headers['status'] != 'RTSP/1.0 200 OK':
            return False, headers['status']
        else:
            if len(headers['Session'].split(';'))  == 2:
                session, timeout = headers['Session'].split(';')
                self.session = session
            elif len(headers['Session'].split(';'))  == 1:
                self.session = headers['Session'].split(';')[0]
        return True, headers['status']
    
    def setup_method_audio(self, s, control):
        # self.debug('{0:*^100}'.format('[setup_method_audio]'))
        url = 'SETUP {}/{} RTSP/1.0\r\nCSeq: {}\r\nSession: {}\r\nTransport: RTP/AVP/TCP;unicast;interleaved=2-3\r\nUser-Agent: Jabsco NVS \r\n\r\n'.format(self.rtsp_url, control, self.cseq, self.session).encode()   # 音频数据请求
        self.debug('[setup_method_audio] {}'.format(url.decode().replace('\r\n', ';')))
        headers, rtv = self.send_data(s, url)
        self.cseq += 1
        if headers['status'] == 'RTSP/1.0 200 OK':
            self.debug('[setup_method_audio] 初始化音频参数')
        return True, headers['status']
    
    def play_method(self, s):
        # self.debug('{0:*^100}'.format('[play_method]'))
        url = 'PLAY {}/ RTSP/1.0\r\nCSeq: {}\r\nSession:  {}\r\nRange: npt=0.000-\r\n\r\n'.format(self.rtsp_url, self.cseq, self.session).encode()
        self.debug('[play_method] {}'.format(url.decode().replace('\r\n', ';')))
        headers, rtv = self.send_data(s, url)
        self.cseq += 1
        if headers['status'] != 'RTSP/1.0 200 OK':
            return False, headers['status']
        else:
            try:
                self.start_timestamp = int(re.findall('rtptime=(\d+)',headers['RTP-Info'])[0])
                self.debug(self.start_timestamp)
            except:
                raise KeyError('start_timestamp not found')
        return True, headers['status']
    
    def async_device_time(self, s):
        pass
    
    def close(self):
        self.s.close()
    
    def connect(self):
        s = socket.socket()
        s.connect((self.ip, self.port))
        self.s = s
        self.username, self.password = None, None
        self.cseq = 1
        r1, msg1 = self.describe_method(s)
        if r1:
            self.debug('[connect] [{}]'.format(msg1))
            video_control = self.sdp_info['video']['control']
            r2, msg2 = self.setup_method_video(s, video_control)
            if r2:
                self.debug('[connect] [{}]'.format(msg2))
                if 'audio' in self.sdp_info:
                    audio_control = self.sdp_info['audio']['control']
                    r3, msg3 = self.setup_method_audio(s, audio_control)
                    if r3:
                        self.debug('[connect] [{}]'.format(msg3))
                        r4, msg4 = self.play_method(s)
                        if r4:
                            self.debug('[connect] [{}]'.format(msg4))
                            self.start = time.time()
                            return True, msg4
                        else:
                            return False, msg4
                else:
                    r4, msg4 = self.play_method(s)
                    if r4:
                        self.debug('[connect] [{}]'.format(msg4))
                        self.start = time.time()
                        return True, msg4
                    else:
                        return False, msg4
            else:
                return False, msg2
        else:
            return False, msg1

    def analysis_info(self, info, dic):
        info = info.strip()
        # self.debug('[analysis_info] {}'.format(info))
        if re.match('a=control:(.*)$', info):
            control = re.findall('control:(.*)$', info)[0]
            dic['control'] = control
        if re.match('.*?framerate:(\d+)', info):
            framerate = re.findall('framerate:(\d+)', info)[0]
            dic['framerate'] = framerate
        if re.match('^a=rtpmap.*$', info):
            val = re.findall('^a=rtpmap:(\d+) (.*?)/(\d+)$', info)[0]
            pt_type,encode_type,timescale=val
            dic['pt_type'] = pt_type
            dic['encode_type'] = encode_type
            dic['timescale'] = timescale
        if re.match('^a=fmtp.*$', info):
            val_list = re.findall('^a=fmtp:\d+ (.*)$', info)[0].split(';')
            for v in val_list:
                index = v.strip().find('=')
                key = v.strip()[0: index]
                val = v.strip()[index+1:]
                dic[key] = val
    
    def get_next(self, l, index):
        if index < len(l):
            return l[index]
        else:
            return False
    
    def analysis_sdp_info(self, sdp):
        index = 0
        res = {}
        sdp = sdp.split('\r\n')
        while index<len(sdp):
            info = self.get_next(sdp, index)
            index += 1
            if re.match('^m=.*?$', info):
                val = re.findall('^m=(.*)$', info)[0].split(' ')
                media_type = val[0].strip()
                res[media_type] = {}
                res[media_type]['pt_type'] = val[3].strip()
                if res[media_type]['pt_type'] == '26':
                    res[media_type]['encode_type'] = 'jpeg'
                while 1:
                    next_info = self.get_next(sdp, index)
                    index += 1
                    if next_info:
                        if re.match('^m=.*?', next_info):
                            index -= 1
                            break
                        else:
                            self.analysis_info(next_info, res[media_type])
                    else:
                        break
        if res['video']['encode_type'] == 'H264':
            self.read_frame = self.read_frame_avc
        elif res['video']['encode_type'] == 'H265':
            self.read_frame = self.read_frame_hevc
        elif res['video']['encode_type'] == 'jpeg':
            self.read_frame = self.read_frame_jpeg
        else:
            raise Exception('unknow rtp data type', res['video']['encode_type'])
        return res
    
    def read_frame_avc(self):
        while True:
            if time.time() - self.start > self.heartbeat_time:
                self.send_heart_beat_pack(self.s, self.session, self.cseq)
                self.cseq += 1
                self.start = time.time()
            rtsp_head = self.s.recv(4)
            retry_index = 0
            while len(rtsp_head) < 4:
                if retry_index > 20:
                    break
                self.debug('[read_frame_avc] rtsp_head: {}'.format(len(rtsp_head)))
                rtsp_head += self.s.recv(4 - len(rtsp_head))
                retry_index += 1
            if rtsp_head == b'RTSP':
                self.debug('[read_frame_avc] RTSP'+self.unpack_rtsp(self.s))
                continue
            elif rtsp_head == b'':
                self.debug('[read_frame_avc] empty data')
                return -1, None
            rtp_data_len = (rtsp_head[2] << 8) + rtsp_head[3]
            rtsp_data = self.s.recv(rtp_data_len)
            while len(rtsp_data) < rtp_data_len:
                rtsp_data += self.s.recv(rtp_data_len - len(rtsp_data))
            if rtsp_head[1] == 0x63:
                self.debug('[read_frame_avc] {}'.format(rtsp_data))
                with open(self.log_path, 'ab+') as fda:
                    fda.write('[ALARM]'.encode() + rtsp_data+'\r\n'.encode())
                continue
            rtp_head = rtsp_data[0:12]
            seq = (rtp_head[2] << 8) + rtp_head[3]
            PT_TYPE = rtp_head[1] & 0x7f
            if PT_TYPE == 96:   # 视频数据
                rtp_idn = rtsp_data[12]
                nal_type = (rtp_idn & 0x1f)
                if nal_type >= 24 :
                    rtp_head_t = rtsp_data[13]
                    rtp_head_type = rtp_head_t & 0x1f
                    S = rtp_head_t >> 7
                    E = (rtp_head_t >> 6) & 0x1
                    if S == 1:
                        frame = []
                        frame_tmp = rtsp_data[14:]
                        frame.append(frame_tmp)
                    else:
                        frame.append(rtsp_data[14:])
                        if E == 1:
                            return rtp_head_type, b''.join(frame)
                else:
                    frame = rtsp_data[12:]
                    return nal_type, frame
            elif PT_TYPE == 0 or PT_TYPE == 8:# ulaw
                audio_type = PT_TYPE
                audio_data = rtsp_data[12:]
                return PT_TYPE, audio_data
            else:
                self.debug('[read_frame_avc] 长度:{}\tPT_TYPE:{}\t{}\tseq:{}'.format(rtp_data_len, PT_TYPE, 'unknow type', seq))
                return -1, None
    
    def read_frame_hevc(self):
        while True:
            if time.time() - self.start > self.heartbeat_time:
                self.send_heart_beat_pack(self.s, self.session, self.cseq)
                self.cseq += 1
                self.start = time.time()
            rtsp_head = self.s.recv(4)
            retry_index = 0
            while len(rtsp_head) < 4:
                if retry_index > 20:
                    break
                self.debug('[read_frame_hevc] rtsp_head: {}'.format(len(rtsp_head)))
                rtsp_head += self.s.recv(4 - len(rtsp_head))
                retry_index += 1
            if rtsp_head == b'RTSP':
                self.debug('[read_frame_hevc] RTSP'+self.unpack_rtsp(self.s))
                continue
            elif rtsp_head == b'':
                self.debug('[read_frame_hevc] empty data')
                return -1,None
            rtp_data_len = (rtsp_head[2] << 8) + rtsp_head[3]
            rtsp_data = self.s.recv(rtp_data_len)
            while len(rtsp_data) < rtp_data_len:
                rtsp_data += self.s.recv(rtp_data_len - len(rtsp_data))
            if rtsp_head[1] == 0x63:
                self.debug('[read_frame_hevc] {}'.format(rtsp_data))
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
                        frame_tmp = rtsp_data[15:]
                        frame.append(frame_tmp)
                    else:
                        frame.append(rtsp_data[15:])
                        if E == 1:
                            return rtp_head_type, b''.join(frame)
                else:   # 单独nal
                    frame = rtsp_data[12:]
                    frame_size = len(frame)
                    return nal_type, frame
            elif PT_TYPE == 0 or PT_TYPE == 8:  # 音频数据
                audio_type = PT_TYPE
                audio_data = rtsp_data[12:]
                return audio_type, audio_data
            else:
                self.debug('[read_frame_hevc] 长度:{}\tPT_TYPE:{}\t{}\tseq:{}'.format(rtp_data_len, PT_TYPE, 'unknow type', seq))
                print(rtsp_data[12:])
                return PT_TYPE, None

    def read_frame_jpeg(self):
        return -1,'typr jpeg not supported'
