import tkinter as tk
from threading import Thread
import socket
import time
import re
import os
import struct
import select
import wave
import logging


SIGN_BIT = 0x80      # Sign bit for a A-law byte. 
QUANT_MASK = 0xf     # Quantization field mask. 
NSEGS = 8            # Number of A-law segments. 
SEG_SHIFT = 4        # Left shift for segment number.
SEG_MASK = 0x70      # Segment field mask. 
BIAS = 0x84          # Bias for linear code.
CLIP = 8159


class Gui:


    def __init__(self):

        logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s][%(levelname)s][%(funcName)s]: %(message)s')
        self.logger = logging.getLogger(__name__)
        self.types = [
            'NAL_TRAIL_N',
            'NAL_TRAIL_R', # 1
            'NAL_TSA_N',
            'NAL_TSA_R',
            'NAL_STSA_N',
            'NAL_STSA_R',
            'NAL_RADL_N',
            'NAL_RADL_R',
            'NAL_RASL_N',
            'NAL_RASL_R',
            '',
            '',
            '',
            '',
            '',
            '',
            'NAL_BLA_W_LP',
            'NAL_BLA_W_RADL', # 17
            'NAL_BLA_N_LP', 
            'NAL_IDR_W_RADL', # 19
            'NAL_IDR_N_LP', # 20
            'NAL_CRA_NUT',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            'NAL_VPS', #32
            'NAL_SPS', #33
            'NAL_PPS', #34
            'NAL_AUD',
            'NAL_EOS_NUT',
            'NAL_EOB_NUT',
            'NAL_FD_NUT',
            'NAL_SEI_PREFIX',
            'NAL_SEI_SUFFIX'
        ]
        
        self.heartbeat_time = 30 # RTSP心跳间隔
        self.record_status = False
        self.root = tk.Tk()
        self.url_entry = tk.Entry(width=30)
        self.url_entry.grid(row=0,column=0,columnspan=2)

        
        streams = [('主码流',1),('从码流',2)]
        self.v=tk.IntVar()
        self.v.set(1)
        i = 0
        for name, stream_type in streams:
            tk.Radiobutton(text=name, value=stream_type, variable=self.v).grid(row=1,column=i)
            i += 1
        
        fix_types = [('视频流', 1), ('音频流', 2)]
        i = 0
        self.check_buttons = []
        for fix_type_name, fix_type in fix_types:
            v_fix = tk.IntVar()
            # v_fix.set(1)
            tk.Checkbutton(text = fix_type_name, variable = v_fix, onvalue = fix_type, offvalue = 0).grid(row=2,column=i)
            i += 1
            self.check_buttons.append(v_fix)
        # self.checkbutton.grid(row=2,column=0,columnspan=2)
        
        self.button = tk.Button(text='录制', command=self.start_record)
        
        self.button.grid(row=3,column=0,columnspan=2)
        self.label = tk.Label()
        
        self.label.grid(row=4,column=0,columnspan=2)
        
        self.text = tk.Text()
        
        # self.text.grid(row=5,column=0,columnspan=2)
        self.root.mainloop()
        
    def alaw2pcm(self, a_val):
        a_val ^= 0x55
        t = (a_val & QUANT_MASK) << 4
        seg = (a_val & SEG_MASK) >> SEG_SHIFT
        if seg == 0:
            t += 8
        elif seg == 1:
            t += 0x108
        else:
            t += 0x108
            t <<= seg - 1
        return t if (a_val & SIGN_BIT) else -t
    
    def ulaw2pcm(self, u_val):
        u_val = ~u_val
        t = ((u_val & QUANT_MASK) << 3) + BIAS
        t <<= (u_val & SEG_MASK) >> SEG_SHIFT
        return (BIAS - t) if (u_val & SIGN_BIT) else (t - BIAS)
    
    def g7112pcm(self, data, PT_TYPE):
        if PT_TYPE == 0:
            return self.ulaw2pcm(data)
        
        elif PT_TYPE == 8:
            return self.alaw2pcm(data)
    
    def count_time(self):
        self.count = 0
        self.label['text'] = '正在录制: {}d - {}h : {:>02}m : {:>02}s'.format(0, 0, 0, 0)
        while self.record_status:
            time.sleep(1)
            self.count += 1
            timestamp = self.get_timestamp(self.count)
            self.label['text'] = '正在录制: '+timestamp
        self.label['text'] = '停止录制: '+timestamp
            
    def get_timestamp(self, count):
        days,hours,mins,ses = 0,0,0,0
        if count >= 86400 :
            days = count // 86400
            count = count % 86400
        if count >= 3600:
            hours = count // 3600
            count = count % 3600
        if count >= 60:
            mins = count // 60
            count = count % 60
        ses = count
        f = '{}d - {}h : {:>02}m : {:>02}s'.format(days, hours, mins, ses)
        return f
    
    def start_record(self):
        ip = self.url_entry.get()
        if len(ip) == 0:
            # print()
            self.logger.error('input err')
            return

        self.logger.debug(ip)
        if self.record_status == False:
            self.button['text'] = '停止'
            self.record_status = True
            #print()
            self.logger.debug(self.v.get())
            self.fix_type = 0
            for i in self.check_buttons:
                self.fix_type += i.get()
            #print()
            self.logger.debug(self.fix_type)
            thread = Thread(target=self.record, args=(ip,))
            thread.start()
        else:
            self.button['text'] = '录制'
            self.record_status = False

    def send_data(self, sock, data):
        sock.send(data)
        rtv = sock.recv(4096)
        return rtv
        


    def send_heart_beat_pack(self, sock, ip, session, cseq):
        data = 'ANNOUNCE rtsp://{}/stream1 RTSP/1.0\r\nCSeq: {}\r\nSession: {}\r\nUser-Agent: Jabsco NVS\r\n\r\n'.format(ip, cseq, session).encode()
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
    
    def connect_rtsp(self, s, ip, stream_type=2):
        # session = ''
        data_list = [
            # 'CMD * RTSP/1.0\r\nCSeq: 1\r\nAccept:TEXT/JCP\r\nContent-Length:19\r\n\r\nversion -act list\r\n'.encode(),
            #' CMD * RTSP/1.0\r\nCSeq: 2\r\nAccept:TEXT/JCP\r\nContent-Length:20\r\n\r\nauthmode -act list\r\n'.encode(),
            # 'CMD * RTSP/1.0\r\nCSeq: 3\r\nAccept:TEXT/JCP\r\nContent-Length:19\r\n\r\nshowweb -act list\r\n'.encode(),
            # 'CMD * RTSP/1.0\r\nCSeq: 4\r\nAccept:TEXT/JCP\r\nContent-Length:20\r\n\r\ndevvecfg -act list\r\n'.encode(),
            # 'CMD * RTSP/1.0\r\nCSeq: 5\r\nAccept:TEXT/JCP\r\nContent-Length:19\r\n\r\nversion -act list\r\n'.encode(),
            # 'CMD * RTSP/1.0\r\nCSeq: 6\r\nAccept:TEXT/JCP\r\nContent-Length:47\r\n\r\ntimecfg -act poweron_sync   -time {} \r\n'.format(str(time.time()).split('.')[0]).encode(),
            'DESCRIBE rtsp://{}:554/stream{} RTSP/1.0\r\nCSeq: 1\r\nAccept: application/sdp\r\nUser-Agent: Jabsco NVS\r\n\r\n'.format(ip, stream_type).encode(),
            'SETUP rtsp://{}:554/stream{}/trackID=1 RTSP/1.0\r\nCSeq: 2\r\nTransport: RTP/AVP/TCP;unicast;interleaved=0-1\r\nUser-Agent: Jabsco NVS \r\n\r\n'.format(ip,stream_type).encode(),
            'SETUP rtsp://{}:554/stream{}/trackID=2 RTSP/1.0\r\nCSeq: 3\r\nSession: {}\r\nTransport: RTP/AVP/TCP;unicast;interleaved=2-3\r\nUser-Agent: Jabsco NVS \r\n\r\n',
            'PLAY rtsp://{}:554/stream{}/ RTSP/1.0\r\nCSeq: 4\r\nSession:  {}\r\nRange: npt=0.000-\r\n\r\n'
        ]
        self.cseq = 1
        for i in range(len(data_list)):
            if i >= 2:
                rtv = self.send_data(s, data_list[i].format(ip, stream_type, self.session).encode())
                self.logger.debug(data_list[i].format(ip, stream_type, self.session))
            else:
                rtv = self.send_data(s, data_list[i])
                self.logger.debug(data_list[i].decode())
            self.logger.debug(rtv.decode())
            if rtv.decode().split('\r\n')[0] != 'RTSP/1.0 200 OK':
                
                return False,rtv.decode().split('\r\n')[0]
            if rtv.decode().split('\r\n')[1].split(':')[1] == ' 2':
                self.session = rtv.decode().split('\r\n')[4].split(';')[0].split(':')[1].strip()
            self.cseq += 1
        return True,''
        
    def record(self, ip):

        self.video_path = ip+'.265'
        self.log_path = 'log/' + ip + '.log'
        self.audio_path = ip+'.pcm'
        
        paths = [self.video_path, self.log_path, self.audio_path]
        
        for path in paths:
            if os.path.exists(path):
                os.remove(path)
            
        fds=[]
        
        if self.fix_type == 3:
            fd = open(self.video_path, 'ab+')
            ad_fd = open(self.audio_path, 'ab+')
            fds.append(fd)
            fds.append(ad_fd)
        elif self.fix_type == 2:
            ad_fd = open(self.audio_path, 'ab+')
            fds.append(ad_fd)
        elif self.fix_type == 1:
            fd = open(self.video_path, 'ab+')
            fds.append(fd)
        
        s = socket.socket()
        s.connect((ip, 554))
        s.settimeout(10)
        fds.append(s)
        stream_type = self.v.get()
        self.label['text']='正在连接RTSP'
        rtv, msg = self.connect_rtsp(s, ip, stream_type)
        if rtv:
            self.label['text'] = '连接RTSP成功'
        else:
            self.label['text'] = msg
            [i.close() for i in fds]
            exit(0)
        
        start = time.time()
        Thread(target=self.count_time).start()
        #print()
        self.logger.info('正在录制 {} stream{}\r\n'.format(ip, stream_type))
        self.text.insert('end','正在录制 {} stream{}\r\n'.format(ip, stream_type))
        p_count = 0
        timeout = 0
        last_time_stamp = 0
        f_1 = struct.Struct('B')
        while self.record_status:
            i_count = 0
            f_read_list = select.select([s,],[],[],5)
            if len(f_read_list) == 0:
                if timeout == 0:
                    timeout = time.time()
                    continue
                else:
                    if time.time() - timeout > 5:
                        self.logger.info('timeout')
                        break

            if time.time() - start > self.heartbeat_time:
                self.send_heart_beat_pack(s, ip, self.session, self.cseq)
                self.cseq += 1
                start = time.time()
            finished_type = '-'
            rtsp_head = s.recv(4)
            while len(rtsp_head) < 4:
                # print('rtsp_head', len(rtsp_head))
                rtsp_head += s.recv(4 - len(rtsp_head))
            if rtsp_head == b'RTSP':
                self.logger.info('RTSP'+self.unpack_rtsp(s))
                continue
            elif rtsp_head == b'':
                self.logger.info('empty data')
                break
            rtp_data_len = (rtsp_head[2] << 8) + rtsp_head[3]
            rtsp_data = s.recv(rtp_data_len)
            while len(rtsp_data) < rtp_data_len:
                rtsp_data += s.recv(rtp_data_len - len(rtsp_data))
            if rtsp_head[1] == 0x63:
                self.logger.info(rtsp_data.decode())
                with open(self.log_path, 'ab+') as fda:
                    fda.write('[ALARM]'.encode() + rtsp_data+'\r\n'.encode())
                continue
            rtp_head = rtsp_data[0:12]
            timestamp = rtsp_data[4:8]
            seq = (rtp_head[2] << 8) + rtp_head[3]
            PT_TYPE = rtp_head[1] & 0x7f
            if PT_TYPE == 96:
                rtp_idn = rtsp_data[12]
                nal_type = (rtp_idn  >> 1) & 0x3f
                if nal_type == 49 : # 分片nal块
                    rtp_head_t = rtsp_data[14]
                    rtp_head_type = rtp_head_t & 0x3f
                    S = rtp_head_t >> 7
                    E = (rtp_head_t >> 6) & 0x1
                    if S == 1:
                        if self.fix_type == 1 or self.fix_type == 3:
                            fd.write(b'\x00\x00\x00\x01')
                            nal_head =  ((rtsp_data[12] & 0b10000000) + (rtp_head_type << 1)) + (rtsp_data[12] & 0b1)  
                            fd.write(f_1.pack(nal_head))
                            fd.write(f_1.pack(rtsp_data[13]))
                            fd.write(rtsp_data[15:])
                        finished_type = 'start'
                        if rtp_head_type == 19 or rtp_head_type == 20:
                            i_count += 1
                            self.logger.info('{} {}'.format(rtp_head_type, self.types[rtp_head_type]))
                        elif rtp_head_type == 1:
                            p_count += 1
                        elif rtp_head_type == 32: # vps
                            self.logger.info('P_FRAME_COUNT {}'.format(p_count))
                    else:
                        if self.fix_type == 1 or self.fix_type == 3:
                            fd.write(rtsp_data[15:])
                        if E == 1:
                            finished_type = 'end'
                else: # 独立nal块
                    if self.fix_type == 1 or self.fix_type == 3:
                        fd.write(b'\x00\x00\x00\x01')
                        fd.write(rtsp_data[12:])
                    if nal_type == 1:
                        p_count += 1
                    else:
                        if nal_type == 32:
                            self.logger.info('P_FRAME_COUNT {}'.format(p_count))
                            p_count = 0
                        if nal_type == 33:
                            pass
                            #print(rtsp_data[12:])
                        self.logger.info('{} {}'.format(nal_type, self.types[nal_type]))            
            elif PT_TYPE == 0 or PT_TYPE == 8:# ulaw
                
                if self.fix_type == 2 or self.fix_type == 3:
                    tmp = []
                    for data in rtsp_data[12:]:
                        tmp.append(struct.pack('h',self.g7112pcm(data, PT_TYPE)))
                    ad_fd.write(b''.join(tmp))
                    self.logger.info('{} {} {}'.format(rtp_data_len, PT_TYPE, 'audio'))
            else:

                self.logger.info('长度:{}\tPT_TYPE:{}\t{}\tseq:{}'.format(rtp_data_len, PT_TYPE, 'unknow type', seq))
        [i.close() for i in fds]
        self.logger.info('stop record')

        self.text.insert('end','录制完成 {} stream{} [{}]\r\n'.format(ip, stream_type,self.get_timestamp(self.count)))
        if self.fix_type == 2 or self.fix_type == 3:
            wav_path = ip + '.wav'
            with open(self.audio_path, 'rb') as fd1:
                pcm_data = fd1.read()
                out_file = wave.open(wav_path, 'wb')
                out_file.setnchannels(1)
                out_file.setframerate(8000)
                out_file.setsampwidth(2) #16-bit
                out_file.writeframesraw(pcm_data)
                out_file.close()


if __name__ == '__main__':
    a = Gui()
        

