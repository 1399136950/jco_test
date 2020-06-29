from record_gui_265 import *
import tkinter as tk
from threading import Thread
import socket
import time
import re
import os
import struct
import select
import wave

class H264Gui(Gui):

    def __init__(self):
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
        
        self.heartbeat_time = 30 # RTSP心跳间隔
        self.record_status = False
        self.root = tk.Tk()
        self.url_entry = tk.Entry(width=30)
        self.url_entry.grid(row=0,column=0,columnspan=2)
        logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s][%(levelname)s][%(funcName)s]: %(message)s')
        self.logger = logging.getLogger(__name__)
        
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


    def record(self, ip):

        self.video_path = ip+'.264'
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
        print('正在录制 {} stream{}\r\n'.format(ip, stream_type))
        self.text.insert('end','正在录制 {} stream{}\r\n'.format(ip, stream_type))
        p_count = 0
        timeout = 0
        last_time_stamp = 0
        while self.record_status:
            i_count = 0
            
            
            f_read_list = select.select([s,],[],[],5)
            
            if len(f_read_list) == 0:
                if timeout == 0:
                    timeout = time.time()
                    
                    continue
                else:
                    if time.time() - timeout > 5:
                        print('timeout')
                        break
                
            
            if time.time() - start > self.heartbeat_time:

                self.send_heart_beat_pack(s, ip, self.session, self.cseq)

                self.cseq += 1
                
                start = time.time()
            
            finished_type = '-'
            
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
            timestamp = rtsp_data[4:8]
            
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
                        now_time_stamp  = struct.unpack('>I', timestamp)[0]
                        # print(now_time_stamp-last_time_stamp)
                        last_time_stamp = now_time_stamp
                        
                        if self.fix_type == 1 or self.fix_type == 3:
                        
                            fd.write(b'\x00\x00\x01')

                            fd.write(struct.pack('B', (rtp_idn & 0xe0) + (rtp_head_t & 0x1f)))

                            fd.write(rtsp_data[14:])
                        
                        finished_type = 'start'

                        if rtp_head_type == 5:

                            i_count += 1
                            
                            # print(self.types[rtp_head_type])
                            self.logger.info('{} {}'.format(rtp_head_type, self.types[rtp_head_type]))
                            # print('P_count',p_count)
                            
                            self.logger.info('P_FRAME_COUNT {}'.format(p_count))
                            
                            p_count = 0
                            
                        elif rtp_head_type == 1:

                            p_count += 1

                    else:
                        if self.fix_type == 1 or self.fix_type == 3:
                            fd.write(rtsp_data[14:])
                        
                        if E == 1:
                            
                            finished_type = 'end'

                else:
                    if self.fix_type == 1 or self.fix_type == 3:
                        fd.write(b'\x00\x00\x00\x01')

                        fd.write(rtsp_data[12:])

                    # print(self.types[nal_type])
                    
                    if nal_type != 1:

                        # print(self.types[nal_type])
                        self.logger.info('{} {}'.format(nal_type, self.types[nal_type]))            
                        if nal_type == 7:
                            # print(rtsp_data[12:])
                            pass
                        
                    else:
                        # print(self.types[nal_type])
                        p_count += 1
                        
                    # print('长度:{}\tPT_TYPE:{}\t{}\t{}\t{}\tseq:{}'.format(rtp_data_len, PT_TYPE, 'video', '单个NAL', self.types[nal_type], seq))
                    
            elif PT_TYPE == 0 or PT_TYPE == 8:# ulaw
                
                if self.fix_type == 2 or self.fix_type == 3:
                    tmp = b''
                    for data in rtsp_data[12:]:
                        tmp += struct.pack('h',self.g7112pcm(data, PT_TYPE))
                    ad_fd.write(tmp)

            else:

                print('长度:{}\tPT_TYPE:{}\t{}\tseq:{}'.format(rtp_data_len, PT_TYPE, 'unknow type', seq))
                # self.logger.info('{} {} {}'.format(rtp_data_len, PT_TYPE, 'audio'))

        [i.close() for i in fds]
        
        print('stop record')
        
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



H264Gui()                
