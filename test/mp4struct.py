import struct
import time
import datetime
import math

class Mp4Struct:

    TIME_1904 = datetime.datetime.strptime("1904-1-01 00:00:00", "%Y-%m-%d %H:%M:%S")
    
    str2int = {
        '0': 0,
        '1': 1,
        '2': 2,
        '3': 3,
        '4': 4,
        '5': 5,
        '6': 6,
        '7': 7,
        '8': 8,
        '9': 9,
        'a': 10,
        'b': 11,
        'c': 12,
        'd': 13,
        'e': 14,
        'f': 15,
        'A': 10,
        'B': 11,
        'C': 12,
        'D': 13,
        'E': 14,
        'F': 15
    }
    
    def __init__(self, filename:str, encode_type:str):
        '''
        encode_type 为 `avc` 或者 `hevc`
        '''
        
        self.encode_type = encode_type
        self.fd = open(filename, 'wb')
        self.offset = 0
        self.set_ftyp()
        # self.set_jcok()
        self.video_stts_object = Stts()
        self.video_stsc_object = Stsc()
        self.video_stsz_object = Stsz()
        self.video_stco_object = Stco()
        self.video_stss_object = Stss()
        self.mdat_obj = Mdat(self.fd)
        self.audio_enable = False   # 音频使能
        self.audio_type = None  # 音频类型
    
    def init_audio_parameter(self): # 初始化音频参数
        self.audio_enable = True
        self.audio_stts_object = Stts()
        self.audio_stsc_object = Stsc()
        self.audio_stsz_object = Stsz()
        self.audio_stco_object = Stco()
        self.audio_stss_object = Stss()

    
    def set_profile_level_id(self, profile_level_id='000000'):
        self.profile_level_id = profile_level_id
    
    def set_audio_type(self, audio_type:int): # audio_type 0  or 8
        if audio_type == 0:
            self.audio_type = 'ulaw'
        elif audio_type == 8:
            self.audio_type = 'alaw'
        else:
            raise Exception('unknow audio type')
            
    def set_sps(self, sps=b''):
        self.sps = sps
        
    def set_pps(self, pps=b''):
        self.pps = pps
        
    def set_vps(self, vps=b''):
        self.vps = vps
    
    def set_width(self, width=0):   # 设置视频宽
        self.width = width
    
    def set_hight(self, hight=0):   # 设置视频高
        self.hight = hight
    
    def get_video_info(self):   # 获取视频分辨率等信息
        return self.width, self.hight, self.sps, self.pps, self.profile_level_id
    
    def close(self):    # 关闭文件
        self.video_sample_delta_count = self.get_video_sample_delta_count()
        if self.audio_enable:
            self.audio_sample_delta_count = self.get_audio_sample_delta_count()
        self.write_mdat()
        self.set_moov()
        self.fd.close()
        print(self.video_sample_delta_count)
    
    def get_video_sample_delta_count(self):
        return self.video_stts_object.sample_delta_count
    
    def get_audio_sample_delta_count(self):
        return self.audio_stts_object.sample_delta_count
    
    def hex_str2int(self, s):   # 将16进制的字符表示形式转为int类型, 例如'4D'转为int是77
        l = len(s)
        sum = 0
        index = l - 1
        for i in range(l):
            sum += self.str2int[s[i]] * (16 ** index)
            index -= 1
        return sum
    
    def make_1904_timestamp(self):  # 创建时间戳,初始值为1904-01-01 00:00:00
        return struct.pack('>L', int((datetime.datetime.now() - self.TIME_1904).total_seconds()))
    
    def set_ftyp(self):
        length = struct.pack('>L', 28)
        ftpe = 'ftyp'.encode()
        major_brand = 'mp42'.encode()
        minor_version = struct.pack('>L', 0)
        compatible_brands = 'mp42isomqt  '.encode()
        # compatible_brands = 'abcdefgjhigj'.encode()
        self.fd.write(length + ftpe + major_brand + minor_version + compatible_brands)
        self.offset += 28
    
    def set_jcok(self):
        jcok = b'\x00\x00\x00\x61\x4A\x43\x4F\x4B\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00\x60\x76\x69\x64\x65\x48\x32\x36\x34\x00\x00\x07\x80\x00\x00\x04\x40\x00\x01\x5F\x90\x00\x00\x00\x19\x5A\x30\x4A\x41\x4B\x4A\x57\x67\x48\x67\x43\x4A\x70\x73\x42\x41\x2C\x61\x4D\x34\x38\x67\x41\x3D\x3D\x00\x00\x00\x61\x73\x6F\x75\x6E\x55\x4C\x41\x57\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1F\x40\x00\x00\x00\x00'
        self.fd.write(jcok)
        self.offset += len(jcok)
    
    
    def set_moov(self):
        moov_len = 0
        moov_head = struct.pack('>L', moov_len) + 'moov'.encode()
        mvhd = self.set_mvhd()
        video_trak = self.set_video_track()
        
        if self.audio_enable:   # 存在audio
            audio_trak = self.set_audio_track()
            moov_len = len(mvhd) + len(video_trak) + len(moov_head) + len(audio_trak)
            moov_head = struct.pack('>L', moov_len) + 'moov'.encode()
            self.fd.write(moov_head)
            self.fd.write(mvhd)
            self.fd.write(video_trak)
            self.fd.write(audio_trak)
        else:   # 不存在audio就只写入video_trak
            moov_len = len(mvhd) + len(video_trak) + len(moov_head)
            moov_head = struct.pack('>L', moov_len) + 'moov'.encode()
            self.fd.write(moov_head)
            self.fd.write(mvhd)
            self.fd.write(video_trak)

    def set_mvhd(self):
        time_unit = 600
        time_len = int((self.video_sample_delta_count/90000)*time_unit)
        new_time = int(time.time())
        mvhd_size = 0
        mvhd_head = struct.pack('>L', mvhd_size) + 'mvhd'.encode()
        versionAndFlag =  struct.pack('I', 0)
        Creation_time = self.make_1904_timestamp()
        Modification_time = self.make_1904_timestamp()
        time_scale = struct.pack('>L', time_unit)
        duration = struct.pack('>L', time_len)
        volume = struct.pack('<H',(1 << 8))
        rate = struct.pack('<I',(1 << 16))
        pading = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        matix_struct = b'\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x40\x00\x00\x00'
        view_time = b'\x00\x00\x00\x00'
        view_duration = b'\x00\x00\x00\x00'
        poster_time = b'\x00\x00\x00\x00'
        selection_time = b'\x00\x00\x00\x00'
        selection_duration = b'\x00\x00\x00\x00'
        now_time = b'\x00\x00\x00\x00'
        next_trackid = b'\x00\x00\x07\xd9'

        info = mvhd_head + versionAndFlag + Creation_time + Modification_time + time_scale + duration + volume + rate \
            + pading + matix_struct + view_time + view_duration + poster_time + selection_time + selection_duration \
            + now_time + next_trackid

        mvhd_size = len(info)
        mvhd_head = struct.pack('>L', mvhd_size) + 'mvhd'.encode()

        info = mvhd_head + versionAndFlag + Creation_time + Modification_time + time_scale + duration + volume + rate \
            + pading + matix_struct + view_time + view_duration + poster_time + selection_time + selection_duration \
            + now_time+next_trackid
        
        return info

    def set_video_track(self):
        track_size = 0
        track_head = struct.pack('>L', track_size) + 'trak'.encode()
        tkhd = self.set_video_tkhd()
        mdia = self.set_video_mdia()
        track_size = len(track_head) + len(tkhd) + len(mdia)
        track_head = struct.pack('>L', track_size) + 'trak'.encode()
        return track_head + tkhd + mdia

    def set_video_tkhd(self):
        time_unit = 600
        tkhd_size = b'\x00\x00\x00\x5c'
        box_type = 'tkhd'.encode()
        version = b'\x00'
        flag = b'\x00\x00\x0f'
        Creation_time = self.make_1904_timestamp()
        Modification_time = self.make_1904_timestamp()
        track_id = struct.pack('>L',96)
        padding = b'\x00\x00\x00\x00'
        duration = struct.pack('>L',time_unit * int(self.video_sample_delta_count/90000))
        layer=b'\x00\x00'
        alternate_group = b'\x00\x00'
        volume = b'\x00\x00'
        matrix_struct = b'\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x40\x00\x00\x00'
        width = struct.pack('>L',self.width << 16)
        height = struct.pack('>L',self.hight << 16)
        return tkhd_size+box_type+version+flag+Creation_time+Modification_time+track_id+padding+duration+padding + \
            padding+layer+alternate_group+volume+b'\x00\x00'+matrix_struct+width+height

    def set_video_mdia(self):
        mdia_size = 0
        mdia_head = struct.pack('>L', mdia_size) + 'mdia'.encode()
        mdhd = self.set_video_mdhd()
        hdlr = self.set_video_hdlr()
        minf = self.set_video_minf()
        mdia_size = len(mdia_head) + len(mdhd) + len(hdlr) + len(minf)
        mdia_head = struct.pack('>L', mdia_size) + 'mdia'.encode()
        return mdia_head + mdhd + hdlr + minf
    
    def set_video_mdhd(self):

        time_unit = 90000
        time_len = int((self.video_sample_delta_count/90000)*time_unit)
        mdhd_size = struct.pack('>L', 32)
        box_type = 'mdhd'.encode()
        version_flag = b'\x00\x00\x00\x00'
        Creation_time = self.make_1904_timestamp()
        Modification_time = self.make_1904_timestamp()
        time_scale = struct.pack('>L', time_unit)
        duration = struct.pack('>L',  time_len)
        language = b'\x00\x00'
        quality = b'\x00\x00'
        return mdhd_size+box_type+version_flag+Creation_time+Modification_time+time_scale+duration+language+quality

    def set_video_hdlr(self):
        box_size = struct.pack('>L', 0)
        box_type = 'hdlr'.encode()
        version_flag = b'\x00\x00\x00\x00'
        component_type = b'\x00\x00\x00\x00'
        component_subtype = 'vide'.encode()
        component_manufacturer = b'\x00\x00\x00\x00'
        component_flags = b'\x00\x00\x00\x00'
        component_flags_mask = b'\x00\x00\x00\x00'
        component_name = b'\x00'
        box_len = len(
            box_size+box_type+version_flag+component_type+component_subtype+component_manufacturer +
            component_flags+component_flags_mask+component_name
        )
        box_size = struct.pack('>L', box_len)
        return box_size+box_type+version_flag+component_type+component_subtype+component_manufacturer+component_flags +\
            component_flags_mask+component_name

    def set_video_minf(self):
        minf_size = 0
        minf_head = struct.pack('>L', minf_size) + 'minf'.encode()
        vmhd = self.set_video_vmhd()
        dinf = self.set_video_dinf()
        stbl = self.set_video_stbl()
        minf_size = len(minf_head) + len(vmhd) + len(dinf) + len(stbl)
        minf_head = struct.pack('>L', minf_size) + 'minf'.encode()
        return minf_head + vmhd + dinf + stbl

    def set_video_vmhd(self):
        box_size = struct.pack('>L', 20)
        box_type = 'vmhd'.encode()
        version = b'\x00'
        flags = b'\x00\x00\x01'
        graphics_mode = b'\x00\x40'
        opcolor = b'\x80\x00\x80\x00\x80\x00'
        return box_size + box_type + version + flags + graphics_mode + opcolor

    def set_video_dinf(self):
        box_len = 0

        dinf_head = struct.pack('>L', box_len) + "dinf".encode()
        
        dref = self.set_video_dref()
        box_len = len(dinf_head) + len(dref)
        dinf_head = struct.pack('>L', box_len) + 'dinf'.encode()
        return dinf_head + dref

    def set_video_dref(self):
        box_len = 0
        box_size = struct.pack('>L', box_len)
        box_type = 'dref'.encode()
        version_flag = b'\x00\x00\x00\x00'
        entry_count = struct.pack('>L', 1)
        
        url = self.set_video_url()
        box_len = len(box_size + box_type + version_flag + entry_count + url)
        box_size = struct.pack('>L', box_len)
        return box_size + box_type + version_flag + entry_count + url
        

    def set_video_url(self):
        box_size = struct.pack('>L', 12)
        box_type = 'url'.encode() + b'\x20'
        version_flags = b'\x00\x00\x00\x01'
        return box_size + box_type + version_flags

    def set_video_stbl(self):
        box_len = 0
        stbl_head = struct.pack('>L', box_len) + 'stbl'.encode()
        
        stsd = self.set_video_stsd()
        stsz = self.get_video_stsz()
        stss = self.get_video_stss()
        stts = self.get_video_stts()
        stco = self.get_video_stco()
        stsc = self.get_video_stsc()
        box_len = len(stbl_head) + len(stsd) + len(stsz) + len(stss) + len(stts) + len(stco) + len(stsc)
        stbl_head = struct.pack('>L', box_len) + 'stbl'.encode()
        return stbl_head + stsd + stts+stsc+stsz + stco + stss

    def set_video_stsd(self):   # encode_type=`avc` or `hevc`
        box_len = 0
        box_size = struct.pack('>L', box_len)
        box_type = 'stsd'.encode()
        version_flag = b'\x00\x00\x00\x00'
        sample_descriptions_count = struct.pack('>L', 1)
        if self.encode_type == 'avc':
            avc1 = self.set_avc1()
            box_len=len(box_size+box_type+version_flag+sample_descriptions_count+avc1)
            box_size = struct.pack('>L', box_len)
            return box_size+box_type+version_flag+sample_descriptions_count+avc1
        elif self.encode_type == 'hevc':
            hvc1 = self.set_hvc1()
            box_len = len(box_size+box_type+version_flag+sample_descriptions_count+hvc1)
            box_size = struct.pack('>L', box_len)
            return box_size+box_type+version_flag+sample_descriptions_count+hvc1
        else:
            raise Exception('unknow stsd type',self.encode_type)

    def set_avc1(self):     # 264编码格式信息
        width, hight, sps, pps, profile_level_id = self.get_video_info()
        box_len = 0
        box_size = struct.pack('>L', box_len)
        box_type = 'avc1'.encode()
        reserved = b'\x00\x00\x00\x00\x00\x00'
        data_reference_index = b'\x00\x01'
        pre_defined = b'\x00\x00'
        reserved_1 = b'\x00\x00'
        pre_defined_1 = b'\x61\x70\x70\x6c\x00\x00\x00\x00\x00\x00\x00\x00'
        width = struct.pack('>H', width)
        hight = struct.pack('>H', hight)
        horizresolution = b'\x00\x48\x00\x00'
        vertresolution  = b'\x00\x48\x00\x00'
        reserved_2 =  b'\x00\x00\x00\x00'
        frame_count = struct.pack('>H', 1)
        compressorname = b'\x05\x48\x2E\x32\x36\x34\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        template = b'\x00\x18'
        pre_defined_2 = b'\xff\xff'

        avcC = self.set_avcC(sps, pps, profile_level_id)

        box_len = len(box_size+box_type+reserved+data_reference_index+pre_defined+reserved_1+pre_defined_1+width+hight +
                  horizresolution + vertresolution+reserved_2+frame_count+compressorname+template+pre_defined_2+avcC)

        box_size = struct.pack('>L', box_len)

        return box_size+box_type+reserved+data_reference_index+pre_defined+reserved_1+pre_defined_1+width+hight + \
            horizresolution+vertresolution+reserved_2+frame_count+compressorname+template+pre_defined_2+avcC

    def set_avcC(self, sps, pps, profile_level_id):    # profile_level_id是长度为6的字符串形式，需要转为16进制
        box_len = 0
        box_size = struct.pack('>L', box_len)
        box_type = 'avcC'.encode()
        version = b'\x01'
        AVC_profile_indication = struct.pack('B', self.hex_str2int(profile_level_id[0:2]))
        AVC_profile_compatibility = struct.pack('B', self.hex_str2int(profile_level_id[2:4]))
        AVC_level_indication = struct.pack('B', self.hex_str2int(profile_level_id[4:]))
        NALU_LEN = b'\xff'
        numOfSequenceParameterSets = b'\xe1'
        sps_len = struct.pack('>H', len(sps))
        sps = sps
        numOfpps = b'\x01'
        pps_len = struct.pack('>H', len(pps))
        pps = pps

        box_len = len(box_size+box_type+version+AVC_profile_indication+AVC_profile_compatibility+AVC_level_indication +
                      NALU_LEN+numOfSequenceParameterSets+sps_len+sps+numOfpps+pps_len+pps)
        box_size = struct.pack('>L', box_len)
        return box_size+box_type+version+AVC_profile_indication+AVC_profile_compatibility+AVC_level_indication + \
            NALU_LEN+numOfSequenceParameterSets+sps_len+sps+numOfpps+pps_len+pps
    
    def set_hvc1(self):     # 265编码格式信息
        box_len = 0
        box_size = struct.pack('>L', box_len)
        box_type = 'hvc1'.encode()
        body = b'\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x61\x70\x70\x6C\x00\x00\x00\x00\x00\x00\x00\x00' + \
            struct.pack('>2H', self.width, self.hight) + \
            b'\x00\x48\x00\x00\x00\x48\x00\x00\x00\x00\x00\x00\x00\x01\x05\x48\x2E\x32\x36\x35\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x18\xFF\xFF'
        hvcC = self.set_hvcC()
        box_len = len(box_size + box_type + body + hvcC)
        box_size = struct.pack('>L', box_len)
        return box_size + box_type + body + hvcC
        
    def set_hvcC(self):
        box_len = 0
        box_size = struct.pack('>L', box_len)
        box_type = 'hvcC'.encode()
        body = b'\x01\x00\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x00\xF0\x00\xFC\xFC\xF8\xF8\x00\x00\x03\x03'
        array1 = self.set_NAL_array(32, self.vps)
        array2 = self.set_NAL_array(33, self.sps)
        array3 = self.set_NAL_array(34, self.pps)
        
        box_len = len(box_size + box_type + body + array1 + array2 + array3)
        box_size = struct.pack('>L', box_len)
        return box_size + box_type + body + array1 + array2 + array3
        
    def set_NAL_array(self, NAL_unit_type, Nal_unit):   # 设置vps/sps/pps信息
        array_completeness = 1  
        reserved = 0
        num_nal_us = b'\x00\x01'
        
        nal_info =  struct.pack(
                'B',
                (array_completeness << 7) + (reserved << 6) + NAL_unit_type
            ) + num_nal_us
        
        nal_config_info = struct.pack('>H', len(Nal_unit)) + Nal_unit
        
        return nal_info + nal_config_info

    def add_video_stts_element(self, sample_delta):
        self.video_stts_object.add_element(sample_delta)
        
    def get_video_stts(self):
        return self.video_stts_object.get_stts()
    
    def add_video_stsz_element(self, sample_size):
        self.video_stsz_object.add_element(sample_size)
        
    def get_video_stsz(self):
        return self.video_stsz_object.get_stsz()
        
    def add_video_stsc_element(self, first_chunk, samples_per_chunk=1, samples_description_index=1):
        self.video_stsc_object.add_element(first_chunk, samples_per_chunk, samples_description_index)
        
    def get_video_stsc(self):
        return self.video_stsc_object.get_stsc()
    
    def add_video_stco_element(self, chunk_offset):
        self.video_stco_object.add_element(chunk_offset)
        
    def get_video_stco(self):
        return self.video_stco_object.get_stco()
    
    def add_video_stss_element(self, sample_number):
        self.video_stss_object.add_element(sample_number)
        
    def get_video_stss(self):
        return self.video_stss_object.get_stss()

    def add_mdat_element(self, mdat_element):
        self.mdat_obj.add_element(mdat_element)
        
    def write_mdat(self):
        mdat_len = self.mdat_obj.write_mdat()
        self.offset += mdat_len
        
    def set_audio_track(self):
        track_size = 0
        track_head = struct.pack('>L', track_size) + 'trak'.encode()
        tkhd = self.set_audio_tkhd()
        mdia = self.set_audio_mdia()
        track_size = len(track_head) + len(tkhd) + len(mdia)
        track_head = struct.pack('>L', track_size) + 'trak'.encode()
        return track_head + tkhd + mdia

    def set_audio_tkhd(self):
        tkhd_size = b'\x00\x00\x00\x5c'
        box_type = 'tkhd'.encode()
        version = b'\x00'
        flag = b'\x00\x00\x0f'
        Creation_time = self.make_1904_timestamp()
        Modification_time = self.make_1904_timestamp()
        track_id = struct.pack('>L', 97)
        padding = b'\x00\x00\x00\x00'
        duration = struct.pack('>L', 1200)
        layer=b'\x00\x00'
        alternate_group = b'\x00\x00'
        volume = b'\x00\x00'
        matrix_struct = b'\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x40\x00\x00\x00'
        width = struct.pack('>L', 0 << 16)
        height = struct.pack('>L', 0 << 16)
        return tkhd_size+box_type+version+flag+Creation_time+Modification_time+track_id+padding+duration+padding + \
            padding+layer+alternate_group+volume+b'\x00\x00'+matrix_struct+width+height

    def set_audio_mdia(self):
        mdia_size = 0
        mdia_head = struct.pack('>L', mdia_size) + 'mdia'.encode()
        mdhd = self.set_audio_mdhd()
        hdlr = self.set_audio_hdlr()
        minf = self.set_audio_minf()
        mdia_size = len(mdia_head) + len(mdhd) + len(hdlr) + len(minf)
        mdia_head = struct.pack('>L', mdia_size) + 'mdia'.encode()
        return mdia_head + mdhd + hdlr + minf
    
    def set_audio_mdhd(self):

        time_unit = 8000
        time_len = int((self.audio_sample_delta_count/time_unit)*time_unit)   # 需要注意区分下
        mdhd_size = struct.pack('>L', 32)
        box_type = 'mdhd'.encode()
        version_flag = b'\x00\x00\x00\x00'
        Creation_time = self.make_1904_timestamp()
        Modification_time = self.make_1904_timestamp()
        time_scale = struct.pack('>L', time_unit)
        duration = struct.pack('>L',  time_len)
        language = b'\x00\x00'
        quality = b'\x00\x00'
        return mdhd_size+box_type+version_flag+Creation_time+Modification_time+time_scale+duration+language+quality

    def set_audio_hdlr(self):
        box_size = struct.pack('>L', 0)
        box_type = 'hdlr'.encode()
        version_flag = b'\x00\x00\x00\x00'
        component_type = 'mhlr'.encode()
        component_subtype = 'soun'.encode()
        component_manufacturer = 'appl'.encode()
        component_flags = b'\x00\x00\x00\x00'
        component_flags_mask = b'\x00\x00\x00\x00'
        component_name = 'Apple Sound Media Handler'.encode()
        component_name_len = struct.pack('B',len(component_name))
        box_len = len(
            box_size+box_type+version_flag+component_type+component_subtype+component_manufacturer +
            component_flags+component_flags_mask+component_name_len+component_name
        )
        box_size = struct.pack('>L', box_len)
        return box_size+box_type+version_flag+component_type+component_subtype+component_manufacturer+component_flags +\
            component_flags_mask+component_name_len+component_name

    def set_audio_minf(self):
        minf_size = 0
        minf_head = struct.pack('>L', minf_size) + 'minf'.encode()
        smhd = self.set_audio_smhd()
        dinf = self.set_audio_dinf()
        stbl = self.set_audio_stbl()
        minf_size = len(minf_head) + len(smhd) + len(dinf) + len(stbl)
        minf_head = struct.pack('>L', minf_size) + 'minf'.encode()
        return minf_head + smhd + dinf + stbl

    def set_audio_smhd(self):
        box_size = struct.pack('>L', 16)
        box_type = 'smhd'.encode()
        version_flags = b'\x00\x00\x00\x00'
        body = b'\x00\x00\x00\x00'
        return box_size + box_type + version_flags + body

    def set_audio_dinf(self):
        box_len = 0
        dinf_head = struct.pack('>L', box_len) + "dinf".encode()
        dref = self.set_audio_dref()
        box_len = len(dinf_head) + len(dref)
        dinf_head = struct.pack('>L', box_len) + 'dinf'.encode()
        return dinf_head + dref

    def set_audio_dref(self):
        box_len = 0
        box_size = struct.pack('>L', box_len)
        box_type = 'dref'.encode()
        version_flag = b'\x00\x00\x00\x00'
        entry_count = struct.pack('>L', 1)
        
        url = self.set_audio_url()
        box_len = len(box_size + box_type + version_flag + entry_count + url)
        box_size = struct.pack('>L', box_len)
        return box_size + box_type + version_flag + entry_count + url
        
    def set_audio_url(self):
        box_size = struct.pack('>L', 12)
        box_type = 'url'.encode() + b'\x20'
        version_flags = b'\x00\x00\x00\x01'
        return box_size + box_type + version_flags

    def set_audio_stbl(self):
        box_len = 0
        stbl_head = struct.pack('>L', box_len) + 'stbl'.encode()
        stsd = self.set_audio_stsd()
        stsz = self.get_audio_stsz()
        stts = self.get_audio_stts()
        stco = self.get_audio_stco()
        stsc = self.get_audio_stsc()
        box_len = len(stbl_head) + len(stsd) + len(stsz) + len(stts) + len(stco) + len(stsc)
        stbl_head = struct.pack('>L', box_len) + 'stbl'.encode()
        return stbl_head + stsd + stts+stsc+stsz + stco

    def set_audio_stsd(self):   # 
        box_len = 0
        box_size = struct.pack('>L', box_len)
        box_type = 'stsd'.encode()
        version_flag = b'\x00\x00\x00\x00'
        sample_descriptions_count = struct.pack('>L', 1)
        if self.audio_type == 'ulaw':
            ulaw = self.set_ulaw()
            box_len=len(box_size+box_type+version_flag+sample_descriptions_count+ulaw)
            box_size = struct.pack('>L', box_len)
            return box_size+box_type+version_flag+sample_descriptions_count+ulaw
        elif self.audio_type == 'alaw':
            alaw = self.set_alaw()
            box_len = len(box_size+box_type+version_flag+sample_descriptions_count+alaw)
            box_size = struct.pack('>L', box_len)
            return box_size+box_type+version_flag+sample_descriptions_count+alaw
        else:
            raise Exception('unknow audio type',self.audio_type)
    
    def set_ulaw(self):
        box_len = 0
        box_size = struct.pack('>L', box_len)
        box_type = 'ulaw'.encode()
        reserved = b'\x00\x00\x00\x00\x00\x00'
        data_reference_index = b'\x00\x01'
        body = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x10\xFF\xFE\x00\x00\x1F\x40\x00\x00'
        box_len = len(box_size+box_type+reserved+data_reference_index+body)
        box_size = struct.pack('>L', box_len)
        return box_size+box_type+reserved+data_reference_index+body
        
    def set_alaw(self):
        box_len = 0
        box_size = struct.pack('>L', box_len)
        box_type = 'alaw'.encode()
        reserved = b'\x00\x00\x00\x00\x00\x00'
        data_reference_index = b'\x00\x01'
        body = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x10\xFF\xFE\x00\x00\x1F\x40\x00\x00'
        box_len = len(box_size+box_type+reserved+data_reference_index+body)
        box_size = struct.pack('>L', box_len)
        return box_size+box_type+reserved+data_reference_index+body
    
    def add_audio_stts_element(self, sample_delta):
        self.audio_stts_object.add_element(sample_delta)
        
    def get_audio_stts(self):
        return self.audio_stts_object.get_stts()
    
    def add_audio_stsz_element(self, sample_size):
        self.audio_stsz_object.add_element(sample_size)
        
    def get_audio_stsz(self):
        return self.audio_stsz_object.get_stsz()
        
    def add_audio_stsc_element(self, first_chunk, samples_per_chunk=1, samples_description_index=1):
        self.audio_stsc_object.add_element(first_chunk, samples_per_chunk, samples_description_index)
        
    def get_audio_stsc(self):
        return self.audio_stsc_object.get_stsc()
    
    def add_audio_stco_element(self, chunk_offset):
        self.audio_stco_object.add_element(chunk_offset)
        
    def get_audio_stco(self):
        return self.audio_stco_object.get_stco()
    
    def add_audio_stss_element(self, sample_number):
        self.audio_stss_object.add_element(sample_number)
        
    def get_audio_stss(self):
        return self.audio_stss_object.get_stss()


        
class Mdat:
    # 数据块
    def __init__(self, fd):
        self.head_len = 8
        self.body = []
        self.body_size = 0
        self.format = struct.Struct('>L')
        self.fd = fd

    def add_element(self, frame):
        self.body.append(frame)
        self.body_size += len(frame)

    def write_mdat(self):
        box_size = self.format.pack(self.head_len + self.body_size)
        box_type = 'mdat'.encode()
        self.fd.write(box_size)
        self.fd.write(box_type)
        self.fd.write(b''.join(self.body))
        return self.head_len + self.body_size    
        
class Stts:

    # 样本播放时长映射表

    def __init__(self):
        self.head_len = 16
        self.entry_len = 0
        self.body = []
        self.body_size = 0
        self.format = struct.Struct('>L')
        self.sample_delta_count = 0
    
    def get_stts(self):

        box_size = self.format.pack(self.head_len + self.body_size)
        box_type = 'stts'.encode()
        version_flag = b'\x00\x00\x00\x00'
        entry_size = self.format.pack(self.entry_len)
        return box_size + box_type + version_flag + entry_size + b''.join(self.body)
        
    def add_element(self, sample_delta):
        # print(sample_delta)
        self.entry_len += 1
        sample_delta_bit = b'\x00\x00\x00\x01' + self.format.pack(sample_delta)
        self.body.append(sample_delta_bit)
        self.sample_delta_count += sample_delta
        self.body_size += len(sample_delta_bit)
        
  
class Stsc:

    # sample和trunk映射表

    def __init__(self):
        self.head_len = 16
        self.entry_len = 0
        self.body = []
        self.body_size = 0
        self.format = struct.Struct('>L')
    
    def get_stsc(self):

        box_size = self.format.pack(self.head_len + self.body_size)
        box_type = 'stsc'.encode()
        version_flag = b'\x00\x00\x00\x00'
        entry_size = self.format.pack(self.entry_len)
        return box_size + box_type + version_flag + entry_size + b''.join(self.body)
        
    def add_element(self, first_chunk, samples_per_chunk, samples_description_index):
        self.entry_len += 1
        element = self.format.pack(first_chunk) + self.format.pack(samples_per_chunk) + self.format.pack(samples_description_index)
        self.body.append(element)
        self.body_size += len(element)
        
        
class Stsz:

    # 样本大小映射表

    def __init__(self):
        self.head_len = 20
        self.entry_len = 0
        self.body = []
        self.body_size = 0
        self.format = struct.Struct('>L')
    
    def get_stsz(self):
        box_size = self.format.pack(self.head_len + self.body_size)
        box_type = 'stsz'.encode()
        version_flag = b'\x00\x00\x00\x00\x00\x00\x00\x00'
        entry_size = self.format.pack(self.entry_len)
        return box_size + box_type + version_flag + entry_size + b''.join(self.body)
        
    def add_element(self, sample_size):
        self.entry_len += 1
        sample_size_bit = self.format.pack(sample_size)
        self.body.append(sample_size_bit)
        self.body_size += len(sample_size_bit)

    
class Stco:

    # chunk位置映射表

    def __init__(self):
        self.head_len = 16
        self.entry_len = 0
        self.body = []
        self.body_size = 0
        self.format = struct.Struct('>L')

    def get_stco(self):

        box_size = self.format.pack(self.head_len + self.body_size)
        box_type = 'stco'.encode()
        version_flag = b'\x00\x00\x00\x00'
        entry_size = self.format.pack(self.entry_len)
        return box_size + box_type + version_flag + entry_size + b''.join(self.body)
        
    def add_element(self, chunk_offset):
        self.entry_len += 1
        chunk_offset_bit = self.format.pack(chunk_offset)
        self.body.append(chunk_offset_bit)
        self.body_size += len(chunk_offset_bit)
        
        
class Stss:
    # I帧对应帧数映射表

    def __init__(self):
        self.head_len = 16
        self.entry_len = 0
        self.body = []
        self.body_size = 0
        self.format = struct.Struct('>L')
        
    def get_stss(self):
        box_size = self.format.pack(self.head_len + self.body_size)
        box_type = 'stss'.encode()
        version_flag = b'\x00\x00\x00\x00'
        entry_size = self.format.pack(self.entry_len)
        return box_size + box_type + version_flag + entry_size + b''.join(self.body)
        
    def add_element(self, sample_index):
        self.entry_len += 1
        sample_index_bit = self.format.pack(sample_index)
        self.body.append (sample_index_bit)
        self.body_size += len(sample_index_bit)
        


class BitArray:

    def __init__(self, data):
        self.str_index = 0
        self.bit_index = 0
        if type(data) != bytes:
            raise TypeError('The type of expectation is bytes')
        self.data = data
        self.data_len = len(data)

    def init(self):
        self.str_index = 0
        self.bit_index = 0 
    
    def read_bit(self, length=1, flag=True):
        res = []
        for i in range(length):
            if self.str_index == self.data_len:
                res = None
                print('end')
                break
            else:
                buff = self.data[self.str_index]
                res.append((buff >> (7 - self.bit_index)) & 1)
                self.bit_index += 1
                if self.bit_index > 7:
                    self.str_index += 1
                    self.bit_index = 0
        if res != None:
            if flag:
                return self.array2bit(res)
            else:
                return res
        return res

    def array2bit(self, arr):
        length = len(arr)
        res = 0
        for i in range(length):
            res += (arr[i] << (length-i-1))
        return res
    
    def get_ue(self): # 无符号哥伦布解码
        index = 0
        while True:
            res = self.read_bit()
            if res == 0:
                index += 1
            else:
                self.bit_index -= 1
                if self.bit_index < 0:
                    self.str_index -= 1
                    self.bit_index = 7
                break
        res = self.read_bit(index+1)
        return res - 1

    def get_se_old(self):   # 有符号哥伦布解码
        index = 0
        while True:
            res = self.read_bit()
            if res == 0:
                index += 1
            else:
                self.bit_index -= 1
                if self.bit_index < 0:
                    self.str_index -= 1
                    self.bit_index = 7
                break
        arr = self.read_bit(index+1, False)
        res = self.array2bit(arr[0:-1])
        if arr[-1] == 1:
            return -1*res
        else:
            return res
            
    def get_se(self):   # 有符号哥伦布解码
        ue_val = self.get_ue()
        se_val = math.ceil(ue_val/2)
        if ue_val % 2 == 0:
            se_val = -se_val
        return se_val

UseDefaultScalingMatrix4x4Flag = [16 for i in range(16)]

UseDefaultScalingMatrix8x8Flag = [16 for i in range(64)]
            
class H264SpsStruct(BitArray):

    def __init__(self, data):
        super().__init__(data)
        self.analysis_sps()
        self.get_width_height()
        
    def analysis_sps_old(self):
        nal_type = self.read_bit(8) & 0b11111
        
        if nal_type != 7:
            raise Exception('nal type not match 7')
            
        self.profile_idc = self.read_bit(8)
        self.constraint_set0_flag = self.read_bit()
        self.constraint_set1_flag = self.read_bit()
        self.constraint_set2_flag = self.read_bit()
        self.constraint_set3_flag = self.read_bit()
        self.reserved_zero_4bits = self.read_bit(4)
        self.level_idc = self.read_bit(8)
        self.seq_parameter_set_id = self.get_ue()
        
        if self.profile_idc in [100, 110, 122, 144]:
            self.chroma_format_idc = self.get_ue()
            if self.chroma_format_idc == 3:
                self.residual_colour_transform_flag = self.read_bit()
                
            self.bit_depth_luma_minus8 = self.get_ue()
            self.bit_depth_chroma_minus8 = self.get_ue()
            self.qpprime_y_zero_transform_bypass_flag = self.read_bit()
            self.seq_scaling_matrix_presend_flag = self.read_bit()
            
            if self.seq_scaling_matrix_presend_flag:
                pass
                
        self.log2_max_frame_num_minus4 = self.get_ue()
        self.pic_order_cnt_type =  self.get_ue()
        
        if self.pic_order_cnt_type == 0:
            self.get_ue()
        elif self.pic_order_cnt_type == 1:
            pass
            
        self.num_ref_frames = self.get_ue()
        self.gaps_in_frame_num_value_allowed_flag = self.read_bit()
        self.pic_width_in_mbs_minus1 = self.get_ue()
        self.pic_height_in_map_units_minus1 = self.get_ue()
        self.frame_mbs_only_flag = self.read_bit()
        
        if not self.frame_mbs_only_flag:
            self.mb_adaptive_frame_field_flag = self.read_bit()
            
        self.direct_8x8_inference_flag = self.read_bit()
        self.frame_cropping_flag = self.read_bit()
        print(self.frame_cropping_flag, 'self.frame_cropping_flag')
        if self.frame_cropping_flag:
            self.frame_crop_left_offset = self.get_ue()
            self.frame_crop_right_offset = self.get_ue()
            self.frame_crop_top_offset = self.get_ue()
            self.frame_crop_bottom_offset = self.get_ue()
            
        self.vui_parameters_present_flag = self.read_bit()
        
        if self.vui_parameters_present_flag:
            pass    # vui_parameters
        # rbsp_trailing_bits()
    
    def analysis_sps(self):
        nal_type = self.read_bit(8) & 0b11111
        if nal_type != 7:
            raise Exception('nal type not match 7')
        self.profile_idc = self.read_bit(8)
        self.constraint_set0_flag = self.read_bit()
        self.constraint_set1_flag = self.read_bit()
        self.constraint_set2_flag = self.read_bit()
        self.constraint_set3_flag = self.read_bit()
        self.constraint_set4_flag = self.read_bit()
        self.constraint_set5_flag = self.read_bit()
        self.reserved_zero_2bits = self.read_bit(2)
        self.level_idc = self.read_bit(8)
        self.seq_parameter_set_id = self.get_ue()
        if self.profile_idc in [100, 110, 122, 244, 44, 83, 86, 118, 128, 138, 139, 134, 135]:
            self.chroma_format_idc = self.get_ue()
            # print(chroma_format_idc)
            if self.chroma_format_idc == 3:
                self.separate_colour_plane_flag = self.read_bit()
            self.bit_depth_luma_minus8 = self.get_ue()
            self.bit_depth_chroma_minus8 = self.get_ue()
            self.qpprime_y_zero_transform_bypass_flag = self.read_bit()
            self.seq_scaling_matrix_present_flag = self.read_bit()
            if self.seq_scaling_matrix_present_flag:
                if self.chroma_format_idc != 3:
                    index = 8
                else:
                    index = 12
                self.seq_scaling_list_present_flag = [None] * index
                for i in range(index):
                    self.seq_scaling_list_present_flag[i] = self.read_bit()
                    if self.seq_scaling_list_present_flag[i]:
                        if i < 6:
                            self.scaling_list(ScalingList4x4[i], 16, UseDefaultScalingMatrix4x4Flag[i])
                        else:
                            self.scaling_list(ScalingList8x8[i - 6], 64, UseDefaultScalingMatrix8x8Flag[i - 6])

            self.log2_max_frame_num_minus4 = self.get_ue()
            self.pic_order_cnt_type = self.get_ue()
            if self.pic_order_cnt_type == 0:
                self.log2_max_pic_order_cnt_lsb_minus4 = self.get_ue()
            elif self.pic_order_cnt_type == 1:
                self.delta_pic_order_always_zero_flag = self.read_bit()
                self.offset_for_non_ref_pic = self.get_se()
                self.offset_for_top_to_bottom_field = self.get_se()
                self.num_ref_frames_in_pic_order_cnt_cycle = self.get_ue()
                for i in range(self.num_ref_frames_in_pic_order_cnt_cycle):
                    self.get_se()
            self.max_num_ref_frames = self.get_ue()
            self.gaps_in_frame_num_value_allowed_flag = self.read_bit()
            self.pic_width_in_mbs_minus1 = self.get_ue()
            self.pic_height_in_map_units_minus1 = self.get_ue()
            print(self.pic_width_in_mbs_minus1, self.pic_height_in_map_units_minus1)
            self.frame_mbs_only_flag = self.read_bit()
            if not self.frame_mbs_only_flag:
                self.mb_adaptive_frame_field_flag = self.read_bit()
            self.direct_8x8_inference_flag = self.read_bit()
            self.frame_cropping_flag = self.read_bit()
            if self.frame_cropping_flag:
                self.frame_crop_left_offset = self.get_ue()
                self.frame_crop_right_offset = self.get_ue()
                self.frame_crop_top_offset = self.get_ue()
                self.frame_crop_bottom_offset = self.get_ue()
            self.vui_parameters_present_flag = self.read_bit()
    
    def scaling_list(self, scalingList, sizeOfScalingList, useDefaultScalingMatrixFlag):
        lastScale = 8
        nextScale = 8
        for j in range(sizeOfScalingList):
            if nextScale != 0:
                delta_scale = self.get_se()
                nextScale = ( lastScale + delta_scale + 256 ) % 256
                useDefaultScalingMatrixFlag = ( j == 0 and nextScale == 0 )
            if nextScale == 0:
                scalingList[j] = lastScale
            else:
                scalingList[j] = nextScale
    
    def get_width_height(self):
        self.width  = (self.pic_width_in_mbs_minus1+1) * 16
        self.height = (2 - self.frame_mbs_only_flag)* (self.pic_height_in_map_units_minus1 +1) * 16
        print(self.width, self.height)
        try:
            self.chroma_format_idc
        except:
            self.chroma_format_idc = 1
            
        if self.frame_cropping_flag:
        
            if 0 == self.chroma_format_idc: # monochrome
                crop_unit_x = 1
                crop_unit_y = 2 - self.frame_mbs_only_flag
            
            elif 1 == self.chroma_format_idc: # 4:2:0
                crop_unit_x = 2
                crop_unit_y = 2 * (2 - self.frame_mbs_only_flag)
            
            elif 2 == self.chroma_format_idc: # 4:2:2
                crop_unit_x = 2
                crop_unit_y = 2 - self.frame_mbs_only_flag
            
            else: # 3 == sps.chroma_format_idc   # 4:4:4
                crop_unit_x = 1
                crop_unit_y = 2 - self.frame_mbs_only_flag

            self.width  -= crop_unit_x * (self.frame_crop_left_offset + self.frame_crop_right_offset)
            self.height -= crop_unit_y * (self.frame_crop_top_offset  + self.frame_crop_bottom_offset)
            

class H265_Nal_Unit(BitArray):

    def __init__(self, data):
        super().__init__(data)
        NumBytesInNalUnit = len(data) - 2
        self.nal_unit(NumBytesInNalUnit)
        
    def nal_unit_header(self):
        self.read_bit(1)
        self.read_bit(6)
        self.read_bit(6)
        self.read_bit(3)

    def nal_unit(self, NumBytesInNalUnit):
        format_s = struct.Struct('B')
        self.nal_unit_header()

        rbsp_byte_array = []
        i = 2
        while i < NumBytesInNalUnit:
            next_bits_24 = self.read_bit(24)
            self.str_index -= 3
            if (i+2 < NumBytesInNalUnit) and next_bits_24 == 0x000003:
                rbsp_byte_array.append( format_s.pack(self.read_bit(8)) )
                rbsp_byte_array.append( format_s.pack(self.read_bit(8)) )
                i += 2
                self.read_bit(8)
            else:
                rbsp_byte_array.append( format_s.pack(self.read_bit(8)) )
            i += 1
        self.rbsp_byte = b''.join(rbsp_byte_array)
        
 
class H265SpsStruct(BitArray):
    
    '''
    data必须是rbsp_byte类型，不能是原始的sps，需要经过H265_Nal_Unit解析
    '''
    
    def __init__(self, data):
        super().__init__(data)
        self.analysis_sps()
        
    def analysis_sps(self):
        sps_video_parameter_set_id = self.read_bit(4)
        sps_max_sub_layers_minus1 = self.read_bit(3)
        sps_temporal_id_nesting_flag = self.read_bit(1)

        self.profile_tier_level(sps_max_sub_layers_minus1)

        sps_seq_parameter_set_id = self.get_ue()
        chroma_format_idc = self.get_ue()

        if chroma_format_idc == 3:
            separate_colour_plane_flag = self.get_ue()

        self.pic_width_in_luma_samples = self.get_ue()
        self.pic_height_in_luma_samples = self.get_ue()
            
    def get_width_height(self):
        return self.pic_width_in_luma_samples, self.pic_height_in_luma_samples
        
    def profile_tier_level(self, maxNumSubLayersMinus1):
        general_profile_space = self.read_bit(2)
        general_tier_flag = self.read_bit(1)
        general_profile_idc = self.read_bit(5)
        general_profile_compatibility_flag = [None]*32
        for i in range(32):
            general_profile_compatibility_flag[i] = self.read_bit(1)
        self.read_bit(4)

        if (general_profile_idc in [4,5,6,7,8,9,10,11]) or general_profile_compatibility_flag[4] or \
        general_profile_compatibility_flag[5] or general_profile_compatibility_flag[6] or \
        general_profile_compatibility_flag[7] or general_profile_compatibility_flag[8] or \
        general_profile_compatibility_flag[9] or general_profile_compatibility_flag[10] or \
        general_profile_compatibility_flag[11]:
            general_max_12bit_constraint_flag = self.read_bit(1)
            general_max_10bit_constraint_flag = self.read_bit(1)
            general_max_8bit_constraint_flag = self.read_bit(1)
            general_max_422chroma_constraint_flag = self.read_bit(1)
            general_max_420chroma_constraint_flag = self.read_bit(1)
            general_max_monochrome_constraint_flag = self.read_bit(1)
            general_intra_constraint_flag = self.read_bit(1)
            general_one_picture_only_constraint_flag = self.read_bit(1)
            general_lower_bit_rate_constraint_flag = self.read_bit(1)

            if (general_profile_idc in [5,9,10,11]) or general_profile_compatibility_flag[5] or \
            general_profile_compatibility_flag[9] or general_profile_compatibility_flag[10] or \
            general_profile_compatibility_flag[11]:
                general_max_14bit_constraint_flag = self.read_bit(1)
                general_reserved_zero_33bits = self.read_bit(33)
            else:
                general_reserved_zero_34bits = self.read_bit(34)
        elif general_profile_idc == 2 or general_profile_compatibility_flag[2]:
            general_reserved_zero_7bits = self.read_bit(7)
            general_one_picture_only_constraint_flag = self.read_bit(1)
            general_reserved_zero_35bits = self.read_bit(35)
        else:
            general_reserved_zero_43bits = self.read_bit(43)
        
        if (general_profile_idc in [1,2,3,4,5,9,11]) or general_profile_compatibility_flag[1] or \
        general_profile_compatibility_flag[2] or general_profile_compatibility_flag[3] or \
        general_profile_compatibility_flag[4] or general_profile_compatibility_flag[5] or \
        general_profile_compatibility_flag[9] or general_profile_compatibility_flag[11]:
            general_inbld_flag = self.read_bit(1)
        else:
            general_reserved_zero_bit = self.read_bit(1)
        
        general_level_idc = self.read_bit(8)
        
        sub_layer_profile_present_flag = [None] * maxNumSubLayersMinus1
        sub_layer_level_present_flag = [None] * maxNumSubLayersMinus1
        for i in range(maxNumSubLayersMinus1):
            sub_layer_profile_present_flag[i] = self.read_bit(1)
            sub_layer_level_present_flag[i] = self.read_bit(1)
            
        if maxNumSubLayersMinus1 > 0:
            for i in range(maxNumSubLayersMinus1, 8):
                self.read_bit(2)
                
        sub_layer_profile_space = [None] * maxNumSubLayersMinus1
        sub_layer_tier_flag = [None] * maxNumSubLayersMinus1
        sub_layer_profile_idc = [None] * maxNumSubLayersMinus1
        
        sub_layer_progressive_source_flag = [None] * maxNumSubLayersMinus1
        sub_layer_interlaced_source_flag = [None] * maxNumSubLayersMinus1
        sub_layer_non_packed_constraint_flag = [None] * maxNumSubLayersMinus1
        sub_layer_frame_only_constraint_flag = [None] * maxNumSubLayersMinus1
        
        sub_layer_profile_compatibility_flag = [ [None] * 32 for i in range(maxNumSubLayersMinus1) ]
        
        sub_layer_max_12bit_constraint_flag = [None] * maxNumSubLayersMinus1
        sub_layer_max_10bit_constraint_flag = [None] * maxNumSubLayersMinus1
        sub_layer_max_8bit_constraint_flag = [None] * maxNumSubLayersMinus1
        sub_layer_max_422chroma_constraint_flag = [None] * maxNumSubLayersMinus1
        sub_layer_max_420chroma_constraint_flag = [None] * maxNumSubLayersMinus1
        sub_layer_max_monochrome_constraint_flag = [None] * maxNumSubLayersMinus1
        sub_layer_intra_constraint_flag = [None] * maxNumSubLayersMinus1
        sub_layer_one_picture_only_constraint_flag = [None] * maxNumSubLayersMinus1
        sub_layer_lower_bit_rate_constraint_flag = [None] * maxNumSubLayersMinus1
        
        sub_layer_max_14bit_constraint_flag = [None] * maxNumSubLayersMinus1
        sub_layer_reserved_zero_33bits = [None] * maxNumSubLayersMinus1
        
        sub_layer_reserved_zero_34bits = [None] * maxNumSubLayersMinus1
        
        sub_layer_reserved_zero_7bits = [None] * maxNumSubLayersMinus1
        sub_layer_one_picture_only_constraint_flag = [None] * maxNumSubLayersMinus1
        sub_layer_reserved_zero_35bits = [None] * maxNumSubLayersMinus1
        
        sub_layer_reserved_zero_43bits = [None] * maxNumSubLayersMinus1
        
        sub_layer_inbld_flag = [None] * maxNumSubLayersMinus1
        
        sub_layer_reserved_zero_bit = [None] * maxNumSubLayersMinus1
        
        sub_layer_level_idc = [None] * maxNumSubLayersMinus1
        
        for i in range(maxNumSubLayersMinus1):
            
            if sub_layer_profile_present_flag[i]:
                sub_layer_profile_space[i] = self.read_bit(2)
                sub_layer_tier_flag[i] = self.read_bit(1)
                sub_layer_profile_idc[i] = self.read_bit(5)
                
                for j in range(32):
                    sub_layer_profile_compatibility_flag[i][j] = self.read_bit(1)
                    
                sub_layer_progressive_source_flag[i] = self.read_bit(1)
                sub_layer_interlaced_source_flag[i] = self.read_bit(1)
                sub_layer_non_packed_constraint_flag[i] = self.read_bit(1)
                sub_layer_frame_only_constraint_flag[i] = self.read_bit(1)
                
                if sub_layer_profile_idc[i] == 4 or \
                sub_layer_profile_compatibility_flag[i][4] or \
                sub_layer_profile_idc[i] == 5 or \
                sub_layer_profile_compatibility_flag[ i ][ 5 ] or \
                sub_layer_profile_idc[ i ] == 6 or \
                sub_layer_profile_compatibility_flag[ i ][ 6 ] or \
                sub_layer_profile_idc[ i ] == 7 or \
                sub_layer_profile_compatibility_flag[ i ][ 7 ] or \
                sub_layer_profile_idc[ i ] == 8 or \
                sub_layer_profile_compatibility_flag[ i ][ 8 ] or \
                sub_layer_profile_idc[ i ] == 9 or \
                sub_layer_profile_compatibility_flag[ i ][ 9 ] or \
                sub_layer_profile_idc[ i ] == 10 or \
                sub_layer_profile_compatibility_flag[ i ][ 10 ] or \
                sub_layer_profile_idc[ i ] == 11 or \
                sub_layer_profile_compatibility_flag[ i ][ 11 ]:
                
                    sub_layer_max_12bit_constraint_flag[ i ] = self.read_bit(1)
                    sub_layer_max_10bit_constraint_flag[ i ] = self.read_bit(1)
                    sub_layer_max_8bit_constraint_flag[ i ] = self.read_bit(1)
                    sub_layer_max_422chroma_constraint_flag[ i ] = self.read_bit(1)
                    sub_layer_max_420chroma_constraint_flag[ i ] = self.read_bit(1)
                    sub_layer_max_monochrome_constraint_flag[ i ] = self.read_bit(1)
                    sub_layer_intra_constraint_flag[ i ] = self.read_bit(1)
                    sub_layer_one_picture_only_constraint_flag[ i ] = self.read_bit(1)
                    sub_layer_lower_bit_rate_constraint_flag[ i ] = self.read_bit(1)
                    
                    if sub_layer_profile_idc[ i ] == 5 or \
                    sub_layer_profile_compatibility_flag[ i ][ 5 ] or \
                    sub_layer_profile_idc[ i ] == 9 or \
                    sub_layer_profile_compatibility_flag[ i ][ 9 ] or \
                    sub_layer_profile_idc[ i ] == 10 or \
                    sub_layer_profile_compatibility_flag[ i ][ 10 ] or \
                    sub_layer_profile_idc[ i ] == 11 or \
                    sub_layer_profile_compatibility_flag[ i ][ 11 ]:
                        sub_layer_max_14bit_constraint_flag[ i ] = self.read_bit(1)
                        sub_layer_reserved_zero_33bits[ i ] = self.read_bit(33)
                    else:
                        sub_layer_reserved_zero_34bits[ i ] = self.read_bit(34)
            elif sub_layer_profile_idc[ i ] == 2 or sub_layer_profile_compatibility_flag[ i ][ 2 ]:
                sub_layer_reserved_zero_7bits[ i ] = self.read_bit(7)
                sub_layer_one_picture_only_constraint_flag[ i ] = self.read_bit(1)
                sub_layer_reserved_zero_35bits[ i ] = self.read_bit(35)
            else:
                sub_layer_reserved_zero_43bits[ i ] = self.read_bit(43)
                
            if sub_layer_profile_idc[ i ] == 1 or \
            sub_layer_profile_compatibility_flag[ i ][ 1 ] or \
            sub_layer_profile_idc[ i ] == 2 or \
            sub_layer_profile_compatibility_flag[ i ][ 2 ] or \
            sub_layer_profile_idc[ i ] == 3 or \
            sub_layer_profile_compatibility_flag[ i ][ 3 ] or \
            sub_layer_profile_idc[ i ] == 4 or \
            sub_layer_profile_compatibility_flag[ i ][ 4 ] or \
            sub_layer_profile_idc[ i ] == 5 or \
            sub_layer_profile_compatibility_flag[ i ][ 5 ] or \
            sub_layer_profile_idc[ i ] == 9 or \
            sub_layer_profile_compatibility_flag[ i ][ 9 ] or \
            sub_layer_profile_idc[ i ] == 11 or \
            sub_layer_profile_compatibility_flag[ i ][ 11 ]:
                sub_layer_inbld_flag[ i ] = self.read_bit(1)
            else:
                sub_layer_reserved_zero_bit[ i ] = self.read_bit(1)
                    
            if  sub_layer_level_present_flag[ i ]:
                sub_layer_level_idc[ i ] = self.read_bit(8)
