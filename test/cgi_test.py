import requests
import re
import math
import sys
from random import randint
from time import sleep, strptime, mktime


from mytelnet import MyTelnet


class CgiTest:

    def __init__(self, ip):
        self.ip = ip
        
        self.jcp2cgi_network = {
            'ethip':'E0.ipaddr',
            'ethmask': 'E0.netmask',
            'ethgw': 'E0.gateway',
            'ethdhcp': 'E0.dhcp',
            'dns': 'E0.dns1',
            'ethmac': 'E0.mac'
        }
        
    def dev_serach_test(self):
        print('{:#^40}'.format('dev_serach_test'))
        cgi_url = 'http://' + self.ip + '/cgi-bin/param.cgi?action=list&group=DEVLIST&devType=4&protocol=0'
        _, res = self.get_http(cgi_url)
        for i in res.split('\r\n'):
            if re.match(r'^root\.DEVLIST\.DO\.devDes=', i):
                ip, logonPort, protolType, usr, channcount, nicindex = re.findall(r"^root\.DEVLIST\.DO\.devDes=(.*?)$",i)[0].split(',')
        portcfg = self.get_jcp_cfg('portcfg')
        ethcfg = self.get_jcp_cfg('ethcfg')
        usercfg = self.get_jcp_cfg('userpasswd')
        if ip !=  ethcfg['ethip']:
            print('{: ^20}'.format('ip err'))
            print(ip)
            print(ethcfg['ethip'])
        if logonPort != portcfg['web']:
            print('{: ^20}'.format('logonPort err'))
            print(logonPort)
            print(portcfg['web'])
        if usr != usercfg['user']:
            print('{: ^20}'.format('usr err'))
            print(usr)
            print(usercfg['user'])

    def get_jcp_cfg(self, model):
        res = {}
        url = 'http://' + self.ip + '/?jcpcmd={} -act list'.format(model)
        _, r = self.get_jcp(url)
        r1 = r.split('[Success]')[1].split(';')
        for i in r1:
            if len(i) > 2:
                key = i.split('=')[0]
                val = i.split('=')[1]
                res[key] = val
        return res
        
    def network_info_test(self):
        print('{:#^40}'.format('network_info_test'))
        cgi_url = 'http://' + self.ip + '/cgi-bin/param.cgi?action=list&group=ETH'
        _, res = self.get_http(cgi_url)
        cgi_dict = {}
        for i in re.split(r'root\.ETH\.|root\.ERR\.', res):
            if i != '':
                key = i.strip().split('=')[0]
                val = i.strip().split('=')[1]
                cgi_dict[key] = val
        jcp_url = 'http://' + self.ip + '/?jcpcmd=ethcfg -act list'
        _, jcp_res = self.get_jcp(jcp_url)
        arr = jcp_res.split('[Success]')[1]
        jcp_dict = {}
        for i in arr.split(';'):
            if len(i)>2:
                key = i.split('=')[0]
                val = i.split('=')[1]
                jcp_dict[key] = val
        for key in self.jcp2cgi_network:
            if jcp_dict[key] != cgi_dict[self.jcp2cgi_network[key]]:
                print('{: ^20}'.format(key+' err'))
                print(jcp_dict[key])
                print(cgi_dict[self.jcp2cgi_network[key]])

    def network_setting_test(self):
        print('{:#^40}'.format('network_setting_test'))
        netmask = '255.255.255.0'
        autoDns = 0
        if randint(999,9999) & 1 == 1:
            ipaddr = '192.168.222.177'
            gateway = '192.168.222.1'
            dns1 = '114.114.114.114'
            dns2 = '8.8.8.8'
        else:
            ipaddr = '192.168.221.177'
            gateway = '192.168.221.1'
            dns2 = '114.114.114.114'
            dns1 = '8.8.8.8'
        
        url = 'http://' + self.ip + '/cgi-bin/param.cgi?action=update&group=ETH&ETH.no=0&ETH.dhcp=0&ETH.ipaddr={}&ETH.netmask={}&ETH.gateway={}&ETH.autoDns={}&ETH.dns1={}&ETH.dns2={}'.format(ipaddr, netmask, gateway, autoDns, dns1, dns2)
        res = self.get_http(url)
        print(res)
        self.ip = ipaddr
        print(ipaddr)
        
        sleep(5)
        jcp_net_cfg = self.get_jcp_cfg('ethcfg')
        print(jcp_net_cfg)
        if jcp_net_cfg['ethip'] == ipaddr and jcp_net_cfg['ethmask'] == netmask:
            if jcp_net_cfg['ethgw'] == gateway and jcp_net_cfg['dns'] == dns1:
                print('设置成功')
            else:
                print('设置异常')
        else:
            print('设置异常')
        
    def get_jcp_video_info(self):
        url='http://' + self.ip + '/?jcpcmd=devvecfg -act list'
        _,r = self.get_jcp(url)
        info_m = re.split('\[Success\]gnum=\d;',r)[1].split('#')[0]
        info_s = re.split('\[Success\]gnum=\d;',r)[1].split('#')[1]
        info_mjpeg = re.split('\[Success\]gnum=\d;',r)[1].split('#')[2]
        m = {}
        s = {}
        mjpeg = {}
        for i in info_m.split(';'):
            if len(i)>0:
                m[i.split('=')[0]]=i.split('=')[1]
        for i in info_s.split(';'):
            if len(i)>0:
                s[i.split('=')[0]]=i.split('=')[1]
        for i in info_mjpeg.split(';'):
            if len(i)>0:
                mjpeg[i.split('=')[0]]=i.split('=')[1]
        return m,s,mjpeg  
        
    def video_info_test(self):
        print('{:#^40}'.format('video_info_test'))
        cgi_url_m = 'http://' + self.ip + '/cgi-bin/param.cgi?action=list&group=VENC&channel=0&streamType=0'
        cgi_url_s = 'http://' + self.ip + '/cgi-bin/param.cgi?action=list&group=VENC&channel=0&streamType=1'
        cgi_url_jpeg = 'http://' + self.ip + '/cgi-bin/param.cgi?action=list&group=VENC&channel=0&streamType=2'
        
        _,res_m = self.get_http(cgi_url_m)
        _,res_s = self.get_http(cgi_url_s)
        _,res_jpeg = self.get_http(cgi_url_jpeg)
        
        cgi_m_cfg = self.get_cgi_cfg(res_m)
        cgi_s_cfg = self.get_cgi_cfg(res_s)
        cgi_jpeg_cfg = self.get_cgi_cfg(res_jpeg)
        
        # print(cgi_jpeg_cfg)
        jcp_m_cfg, jcp_s_cfg,_ = self.get_jcp_video_info()
        jcp_audio_cfg = self.get_jcp_cfg('audiocfg')
        # print(cgi_m_cfg, cgi_s_cfg)
        # print(jcp_audio_cfg)
        
        jcp2cgi_codec = {
            '2': '0',
            '5': '1',
            '7': '4'
        }
        jcp2cgi_fixbps = {
            '0': '1',
            '1': '0'
        }
        
        key_set = (
            'root.VENC.streamMixType',
            'root.VENC.h264EncLvl',
            'root.VENC.frameRate',
            'root.VENC.frPreeferred',
            'root.VENC.iFrameIntv',
            'root.VENC.veType',
            'root.VENC.bitRate',
            'root.VENC.bitRateType',
            'root.VENC.quality',
            'root.VENC.resolution',
            'root.VENC.standard',
            'root.VENC.iQp',
            'root.VENC.pQp',
            'root.VENC.audioInputMode',
            'root.VENC.audioEncType',
            'root.VENC.audioInputGain',
            'root.VENC.audioOutputGain'
        )
        
        print('主码流')
        m_exists_key = []
        for key in cgi_m_cfg:
            # print(key)
            m_exists_key.append(key)
            if key == 'root.VENC.frameRate':
                if cgi_m_cfg[key] != jcp_m_cfg['fps']:
                    print('{: ^20}'.format('fps err'))
                    print(cgi_m_cfg[key])
                    print(jcp_m_cfg['fps'])
                    
            if key == 'root.VENC.iFrameIntv':
                if cgi_m_cfg[key] != jcp_m_cfg['gop']:
                    print('{: ^20}'.format('gop err'))
                    print(cgi_m_cfg[key])
                    print(jcp_m_cfg['gop'])
                    
            if key == 'root.VENC.veType':
                if cgi_m_cfg[key] != jcp2cgi_codec[jcp_m_cfg['codec']]:
                    print('{: ^20}'.format('codec err'))
                    print(cgi_m_cfg[key])
                    print(jcp2cgi_codec[jcp_m_cfg['codec']])
                    
            if key == 'root.VENC.bitRate':
                if cgi_m_cfg[key] != jcp_m_cfg['bps']:
                    print('{: ^20}'.format('bps err'))
                    print(cgi_m_cfg[key])
                    print(jcp_m_cfg['bps'])
                    
            if key == 'root.VENC.bitRatype':
                if cgi_m_cfg[key] != jcp2cgi_fixbps[jcp_m_cfg['fixbps']]:
                    print('{: ^20}'.format('fixbps err'))
                    print(cgi_m_cfg[key])
                    print(jcp2cgi_fixbps[jcp_m_cfg['fixbps']])
                    
            if key == 'root.VENC.standard':
                if cgi_m_cfg[key] != jcp_m_cfg['standard']:
                    print('{: ^20}'.format('standard err'))
                    print(cgi_m_cfg[key])
                    print(jcp_m_cfg['standard'])
                    
            if key == 'root.VENC.audioInputMode':   #   0:Mic,1:Line
                if cgi_m_cfg[key] != jcp_audio_cfg['inputtype']:
                    print('{: ^20}'.format('inputtype err'))
                    print(cgi_m_cfg[key])
                    print(jcp_audio_cfg['inputtype'])
                
            if key == 'root.VENC.audioEncType':     #   0:PCM, 1:G711A, 2:G711U
                if cgi_m_cfg[key] != jcp_audio_cfg['codetype']:
                    print('{: ^20}'.format('codetype err'))
                    print(cgi_m_cfg[key])
                    print(jcp_audio_cfg['codetype'])
                
            if key == 'root.VENC.audioInputGain':
                if cgi_m_cfg[key] != str(math.floor(int(jcp_audio_cfg['involume'])/10)):
                    print('{: ^20}'.format('involume err'))
                    print(cgi_m_cfg[key])
                    print(jcp_audio_cfg['involume'])
            if key == 'root.VENC.audioOutputGain':
                if cgi_m_cfg[key] != str(math.floor(int(jcp_audio_cfg['outvolume'])/10)):
                
                    print('{: ^20}'.format('outvolume err'))
                    print(cgi_m_cfg[key])
                    print(jcp_audio_cfg['outvolume'])
        
        print('从码流')
        s_exists_key = []        
        for key in cgi_s_cfg:
            s_exists_key.append(key)
            if key == 'root.VENC.frameRate':
                if cgi_s_cfg[key] != jcp_s_cfg['fps']:
                    print('{: ^20}'.format('fps err'))
                    print(cgi_s_cfg[key])
                    print(jcp_s_cfg['fps'])
                    
            if key == 'root.VENC.iFrameIntv':
                if cgi_s_cfg[key] != jcp_s_cfg['gop']:
                    print('{: ^20}'.format('gop err'))
                    print(cgi_s_cfg[key])
                    print(jcp_s_cfg['gop'])
                    
            if key == 'root.VENC.veType':
                if cgi_s_cfg[key] != jcp2cgi_codec[jcp_s_cfg['codec']]:
                    print('{: ^20}'.format('codec err'))
                    print(cgi_s_cfg[key])
                    print(jcp2cgi_codec[jcp_s_cfg['codec']])
                    
            if key == 'root.VENC.bitRate':
                if cgi_s_cfg[key] != jcp_s_cfg['bps']:
                    print('{: ^20}'.format('bps err'))
                    print(cgi_s_cfg[key])
                    print(jcp_s_cfg['bps'])
                    
            if key == 'root.VENC.bitRatype':
                if cgi_s_cfg[key] != jcp2cgi_fixbps[jcp_s_cfg['fixbps']]:
                    print('{: ^20}'.format('fixbps err'))
                    print(cgi_s_cfg[key])
                    print(jcp2cgi_fixbps[jcp_s_cfg['fixbps']])
                    
            if key == 'root.VENC.standard':
                if cgi_s_cfg[key] != jcp_s_cfg['standard']:
                    print('{: ^20}'.format('standard err'))
                    print(cgi_s_cfg[key])
                    print(jcp_s_cfg['standard'])
                    
            if key == 'root.VENC.audioInputMode':   #   0:Mic,1:Line
                if cgi_s_cfg[key] != jcp_audio_cfg['inputtype']:
                    print('{: ^20}'.format('inputtype err'))
                    print(cgi_s_cfg[key])
                    print(jcp_audio_cfg['inputtype'])
                
            if key == 'root.VENC.audioEncType':     #   0:PCM, 1:G711A, 2:G711U
                if cgi_s_cfg[key] != jcp_audio_cfg['codetype']:
                    print('{: ^20}'.format('codetype err'))
                    print(cgi_s_cfg[key])
                    print(jcp_audio_cfg['codetype'])
                
            if key == 'root.VENC.audioInputGain':
                if cgi_s_cfg[key] != str(math.floor(int(jcp_audio_cfg['involume'])/10)):
                    print('{: ^20}'.format('involume err'))
                    print(cgi_s_cfg[key])
                    print(jcp_audio_cfg['involume'])
            if key == 'root.VENC.audioOutputGain':
                if cgi_s_cfg[key] != str(math.floor(int(jcp_audio_cfg['outvolume'])/10)):
                    print('{: ^20}'.format('outvolume err'))
                    print(cgi_s_cfg[key])
                    print(jcp_audio_cfg['outvolume'])
              
        for k in key_set:
            if k not in m_exists_key:
                print('m lost key',k)
            
            if k not in s_exists_key:
                print('s lost key',k)
        
    
    def get_cgi_cfg(self, res):
        cgi_dict = {}
        for i in res.split('\r\n'):
            if i != '':
                key = i.strip().split('=')[0]
                val = i.strip().split('=')[1]
                cgi_dict[key] = val
        return cgi_dict
    
    def video_setting_test(self):
        print('{:#^40}'.format('video_setting_test'))
        
        streamType = str(randint(0,2))   #   0 主碼流 1-次碼流 2-三碼流
        h264EncLvl = str(randint(0,2))   #   編碼等級：0 - baseline profile, 1 - main profile, 2 - high profile
        frameRate = str(randint(10,30))
        frPreeferred = str(randint(0,1)) #   是否幀率優先 1: 是, 0: 不是
        
        if streamType == '2':
            veType =  '1'  #   視頻編碼類型0：H.264,1：MJPEG,2：JPEG,3：MPEG4 4：H.265
            frameRate = str(randint(1,10))
        else:
            veType = ['0','4'][randint(1,10) & 1]
        iFrameIntv = str(int(frameRate)*2)    #   I帧间隔
        bitRate = str(randint(2048,4096))
        bitRateType = str(randint(0,1))  #   碼率類型:   0 - 定碼流, 1 - 變碼流, 2 - 按品質編碼
        quality = str(randint(0,2))
        resolution = '65535'
        standard = str(randint(0,1)) #   0 - P制,1 - N制
        audioInputMode = str(randint(0,1))   #   0 - MIC輸入,1 - 線輸入
        audioEncType = str(randint(1,2)) #   1:g711a, 2:g711u
        audioInputGain = str(randint(1,100))
        audioOutputGain = str(randint(1,100))
        # print(audioInputGain,audioOutputGain)
        url = 'http://' + self.ip + '/cgi-bin/param.cgi?action=update&group=VENC&&channel=0&streamType={}&VENC.streamMixType=0&VENC.h264EncLvl={}&VENC.frameRate={}&VENC.frPreeferred={}&VENC.iFrameIntv={}&VENC.veType={}&VENC.bitRate={}&VENC.bitRateType={}&VENC.quality={}&VENC.resolution={}&VENC.standard={}&VENC.audioInputMode={}&VENC.audioInputGain={}&VENC.audioOutputGain={}&VENC.audioEncType={}'.\
        format(streamType, h264EncLvl, frameRate, frPreeferred, iFrameIntv, veType, bitRate, bitRateType, quality, resolution, standard, audioInputMode, audioInputGain, audioOutputGain, audioEncType)
        _, res = self.get_http(url)
        print(url)
        print(res)
        
        

        video_info = self.get_jcp_video_info()
        jcp_audio_cfg = self.get_jcp_cfg('audiocfg')

        if streamType == '0':
            jcp_video_cfg = video_info[0]
        elif streamType == '1':
            jcp_video_cfg = video_info[1]
        elif streamType == '2':
            jcp_video_cfg = video_info[2]

        
        _, profile_info = self.get_jcp('http://'+ self.ip + '/?jcpcmd=veprofile -act list')
        print(profile_info)
        print(jcp_video_cfg['vencsize'])
        try:
            jcp_video_cfg['profile'] = re.findall('vesize={};profile=(\d+)'.format(jcp_video_cfg['vencsize']), profile_info)[0]
        except Exception as e:
            print(e)
        
        print(jcp_video_cfg)
        print(jcp_audio_cfg)
        
        cgi2jcp_codec = {
            '0': '2',
            '1': '5',
            '4': '7'
        }
        cgi2jcp_fixbps = {
            '0': '1',
            '1': '0',
            '2': 'None'
        }
        cgi2jcp_profile = {
            '0': '2',
            '1': '1',
            '2': '0'
        }
        for key in jcp_video_cfg:
            if key == 'codec':
                if jcp_video_cfg[key] != cgi2jcp_codec[veType]:
                    print(key,'err')
                    print(jcp_video_cfg[key])
            if key == 'standard':
                if jcp_video_cfg[key] != standard:
                    print(key,'err')
                    print(jcp_video_cfg[key])
            if key == 'fps':
                if jcp_video_cfg[key] != frameRate:
                    print(key,'err')
                    print(jcp_video_cfg[key])
            if key == 'bps':
                if jcp_video_cfg[key] != bitRate:
                    print(key,'err')
                    print(jcp_video_cfg[key])
            if key == 'gop':
                if jcp_video_cfg[key] != iFrameIntv:
                    print(key,'err')
                    print(jcp_video_cfg[key])
            if key == 'fixbps': #  
                if jcp_video_cfg[key] != cgi2jcp_fixbps[bitRateType]:
                    print(key,'err')
                    print(jcp_video_cfg[key])
            if key == 'profile': # 
                if jcp_video_cfg[key] != cgi2jcp_profile[h264EncLvl]:
                    print(key,'err')
                    print(jcp_video_cfg[key])

                
        for key in jcp_audio_cfg:
            if key == 'inputtype': #  
                if jcp_audio_cfg[key] != audioInputMode:
                    print(key,'err')
                    print(jcp_audio_cfg[key])
            if key == 'involume': #   
                if jcp_audio_cfg[key] != audioInputGain:
                    print(key,'err')
                    print(jcp_audio_cfg[key])
                    print(audioInputGain)
            if key == 'outvolume': #  
                if jcp_audio_cfg[key] != audioOutputGain:
                    print(key,'err')
                    print(jcp_audio_cfg[key])
                    print(audioOutputGain)
            if key == 'codetype': #  
                if jcp_audio_cfg[key] != audioEncType:
                    print(key,'err')
                    print(jcp_audio_cfg[key])
                    print(audioEncType)
                    
                
    def record_search_test(self):
        print('{:#^40}'.format('record_search_test'))
        url = 'http://' + self.ip +'/cgi-bin/record.cgi?action=list&group=RECORD&channel=0&beginTime={}&endTime={}&type=4294967295&beginNo=0&reqCount={}&sessionId={}'
        res = self.get_record_dir()
        print(res)
        for i in res:
            print('{:-^80}'.format(i))
            start_str = '{}-{}-{} 00:00:00'.format(i[0:4],i[4:6],i[6:])
            if i == '19700101':
                start_str = '{}-{}-{} 08:00:00'.format(i[0:4],i[4:6],i[6:])
                
            end_str = '{}-{}-{} 23:59:59'.format(i[0:4],i[4:6],i[6:])
            
            print(start_str, end_str)
            
            start_stamp = self.get_time_stamp(start_str) + 28800
            end_stamp = self.get_time_stamp(end_str) +28800
            print(start_stamp, end_stamp)
            path = '/opt/media/mmcblk0p1/IPCamera/' + i + '/'
            print(path)
            file_list = self.get_video_file_info(path)
            print("true totalCount: ",len(file_list))  
            new_url = url.format(start_stamp, end_stamp, 5, 0)
            
            _, res = self.get_http(new_url)
            
            record = self.analysis_record_response(res)

            try:
                record['totalCount']
            except:
                print(new_url)
                print(record)
            else:
                print(record['totalCount'])
                if record['totalCount'] == record['rspCount']:
                    # record['record']
                    if len(record['record']) > 0:
                        for key in record['record']:
                            tmp = record['record'][key]
                            print(tmp)
                else:
                    new_url = url.format(start_stamp, end_stamp, record['totalCount'], record['sessionId'])
                    _, new_res = self.get_http(new_url)
                    new_record = self.analysis_record_response(new_res)
                    if len(new_record['record']) > 0:
                        for key in new_record['record']:
                            tmp = new_record['record'][key]
                            print(tmp)
                        print("response totalCount: ",new_record['totalCount'])    
                print(new_url)


                
    
    def analysis_record_response(self, response):
        record = {}
        record['record'] = {}
        for i in response.split('\r\n'):
            if len(i) > 0:
                # print(i)
                if re.match('^root\.RECORD\.sessionId',i):
                    record['sessionId'] = i.split('=')[1]
                if re.match('^root\.RECORD\.totalCount',i):
                    record['totalCount'] = i.split('=')[1]
                if re.match('^root\.RECORD\.rspCount',i):
                    record['rspCount'] = i.split('=')[1]
                if re.match('^root\.RECORD\.ITEM\d+',i):
                    key = re.findall('(ITEM\d+)', i)[0]
                    try:
                        record['record'][key]
                    except:
                        record['record'][key] = {}
                    finally:
                        attr = re.findall('ITEM\d+\.(.*)=.*',i)[0]
                        val = i.split('=')[1]
                        record['record'][key][attr] = val  
                if re.match('^root\.ERR\.no',i):
                    record['no'] = i.split('=')[1]
                if re.match('^root\.ERR\.des',i):
                    record['des'] = i.split('=')[1]
                if re.match('^returnCode',i):
                    record['returnCode'] = i.split('=')[1]
                if re.match('^returnDes',i):
                    record['returnDes'] = i.split('=')[1]
        return record
    
    def get_time_stamp(self, src_str):
        timeArray = strptime(src_str, "%Y-%m-%d %H:%M:%S")
        stamp = int(mktime(timeArray))
        return stamp
    
    def get_video_file_info(self, path):
        record_type = {
            'A': '2',
            'S': '1',
            'M': '8'
        }
        tel = MyTelnet(self.ip, 24)
        tel.login()
        cmd = "ll " + path + " --color=never|egrep 'mp4$'|awk '{print $5,$9}'"
        res = tel.write(cmd, 1).split('\r\n')
        file_list = []
        date = re.findall('\d{8}', path)[0]
        for i in res:
            if re.match('^\d+.*mp4$', i):
                file_info = {}
                size,filename = i.split(' ')
                type, start_time, record_time_size = filename.split('.')[0].split('-')
                # file_list.append(file_info)
                beginTime_str = '{}-{}-{} {}:{}:{}'.format(date[0:4], date[4:6], date[6:], start_time[0:2], start_time[2:4], start_time[4:])
                file_info['beginTime'] = str(self.get_time_stamp(beginTime_str))
                file_info['size']      = size
                file_info['endTime']   = str(self.get_time_stamp(beginTime_str)+int(record_time_size))
                file_info['type']      = record_type[type]
                print(file_info)
                file_list.append(file_info)
                # beginTime endTime type size
        return file_list
        
    def get_record_dir(self):
        tel = MyTelnet(self.ip, 24)
        tel.login()
        PATH = '/opt/media/mmcblk0p1/IPCamera/'
        res = tel.write('ls {} --color=never|xargs -n1'.format(PATH),1)
        record_dir_list = res.split('\r\n')[1:-1]
        for i in record_dir_list:
            if not re.match('^\d{8}$', i):
                record_dir_list.remove(i)
        return record_dir_list
    
    def get_rtsp_url_test(self):
        print('{:#^40}'.format('get_rtsp_url_test'))
        url_m = 'http://' + self.ip + '/cgi-bin/video.cgi?action=list&group=RTSP&channel=0'
        url_s = 'http://' + self.ip + '/cgi-bin/video.cgi?action=list&group=RTSP&channel=1'
        url_mjpeg = 'http://' + self.ip + '/cgi-bin/video.cgi?action=list&group=RTSP&channel=2'
        _,r_m = self.get_http(url_m)
        _,r_s = self.get_http(url_s)
        _,r_mjpeg = self.get_http(url_mjpeg)
        print('rtsp url: master:',r_m)
        print('rtsp url: slaver:',r_s)
        print('rtsp url: mjpeg:',r_mjpeg)
    
    def snap_test(self):
        print('{:#^40}'.format('snap_test'))
        url='http://' + self.ip + '/cgi-bin/snap.cgi?channel=0'
        r = requests.get(url)
        with open('test.jpeg','wb') as fd:
            fd.write(r.content)

    def get_http(self, url):
        r = requests.get(url)
        return r.status_code, r.text
        
    def get_jcp(self, url):
        r = requests.get(url, cookies=dict(loginflag='1'))
        return r.status_code, r.text


if __name__ == '__main__':
    ip = sys.argv[1]
    a = CgiTest(ip)
    
    # a.network_setting_test()
    a.network_info_test()
    a.dev_serach_test()
    a.snap_test()
    a.get_rtsp_url_test()
    a.video_setting_test()
    a.video_info_test()
    '''
    a.record_search_test()
    '''