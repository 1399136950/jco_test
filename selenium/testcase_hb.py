import unittest
import requests
import json
import re
import os
import sys
from selenium import webdriver
from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from testbase import TestBase


class HbTest(TestBase, unittest.TestCase):
    langeuage_file='language.json'
    @classmethod
    def setUpClass(self):
        self.result={}
        driver=webdriver.Ie()
        driver.maximize_window()
        driver.get('http://'+self.IP)
        self.driver=driver
        try:
            WebDriverWait(driver,20,0.5).until(EC.presence_of_element_located((By.ID,"ID_LANGUAGE")))
        except:
            print('err')
        else:
            sleep(0.5)
            myselect = Select(self.driver.find_element_by_id("ID_LANGUAGE"))
            print("默认语言   : ",myselect.first_selected_option.text)
            self.result['language']=myselect.first_selected_option.text
            self.result['ocx_url']= driver.find_element_by_id("ID_DOWNLOAD_LINK_MANUAL").get_attribute("href")
            print('插件地址   : ',self.result['ocx_url'])
            
            js='document.getElementById("' + 'log_login' + '").click()'
            self.driver.execute_script(js)
            sleep(1)
            self.user_info=[['admin','888888'],['admin','admin'],['admin','admin12345'],['admin','admin123456'],['admin','123456'],['admin','12345'],['user','user'],['test','test']]#预存放的账户密码
            try:
                a1=self.driver.switch_to.alert
            except:
                pass
            else:
                a1.accept()
                self.handle_with_alter(self)  
            try:
                WebDriverWait(driver,20,0.5).until(EC.presence_of_element_located((By.ID,"spanSetting")))
            except:
                print('no')
            else:
                sleep(0.5)
                self.driver.find_element_by_xpath("/html/body/div[@class='bd']/div[@class='side']").click()
                self.driver.find_element_by_xpath("/html/body/div[@class='bd']/div[@class='side']/div[@class='banner']/span[@id='spanSetting']").click()
                sleep(1)
                self.ip=self.IP
                with open(self.langeuage_file,encoding='utf-8') as file:
                    self.title=json.load(file)
                sleep(1)
       
    @classmethod
    def tearDownClass(self):
        print('out')
        self.driver.close()
        self.driver.quit()
        
    def handle_with_alter(self):
        load_state=False
        for data in self.user_info:
            self.driver.find_element_by_id("loginuserName").send_keys(data[0])
            self.driver.find_element_by_id("loginpasswd").send_keys(data[1])
            js='document.getElementById("' + 'log_login' + '").click()'
            self.driver.execute_script(js)
            sleep(1)
            try:
                a=self.driver.switch_to.alert
            except:
                load_state=data
                break
            else:
                a.accept()
                self.driver.find_element_by_id("loginuserName").clear()
                self.driver.find_element_by_id("loginpasswd").clear()     
        if load_state:
            print(load_state)
            self.result['user_pwd']=load_state
        else:
            print('未知密码')
            self.driver.quit()
            sys.exit()

    def MyClickById(self,id):
        try:
            self.driver.find_element_by_id(id).click()
        except:
            print("can't click")
        
    def GetValueById(self,id):#获取value参数	
        try:
            return self.driver.find_element_by_id(id).get_attribute("value")
        except:
            return 'EMPTY'
		
    def GetTextById(self,id):
        try:
            return self.driver.find_element_by_id(id).text
        except:
            return 'EMPTY'
		
    def GetFirstSelectedById(self,id):
        try:
            myselect = Select(self.driver.find_element_by_id(id))
        except:
            return 'EMPTY';
        else:
            return myselect.first_selected_option.text
	
    def IsSelectedById(self,id):
        try:
            self.driver.find_element_by_id(id)
        except:
            return -1
        else:
            return self.driver.find_element_by_id(id).is_selected()
            
    def IsDisplayById(self,id):
        try:
            element=self.driver.find_element_by_id(id)
        except:
            return -1
        else:
            return element.is_displayed()
	
    def model_init(self,model):
        model_id={}
        model_id['sub1Span']='pop1'
        model_id['sub2Span']='pop2'
        model_id['sub3Span']='pop3'
        model_id['sub4Span']='pop4'
        model_id['sub5Span']='pop5'
        model_id['sub6Span']='pop6'
        model_id['sub7Span']='pop7'
        model_id['sub8Span']='pop8'
        try:
            WebDriverWait(self.driver,20,0.5).until(EC.presence_of_element_located((By.ID, model)))
        except:
            return 'EMPTY'
        else:	
            self.MyClickById(model)
            ul=self.driver.find_element_by_id(model_id[model]).find_elements_by_class_name("secondclassdiv")
            self.driver.find_element_by_xpath("/html/body/div[@class='bd']/div[@class='main']").click()
            return ul

    def test_sysset(self):

        ul=self.model_init("sub1Span")
        for li in ul:
            if(len(li.text)>0):
                if(li.text in self.title["BASCIINFO"]):
                    li.click()
                    sleep(1)
                    self.driver.find_element_by_id("homeFrame")	
                    self.driver.switch_to.frame("homeFrame")
                    print('        [基本信息]:')
                    HbTest.version=self.GetTextById("server_bb")
                    print('服务版本 : ',self.version)
                    print('设备名称 : ',self.GetValueById("dev_name"))
                    print('设备型号 : ',self.GetTextById("dev_model"))
                    self.result['version']=HbTest.version
                    self.result['dev_name']=self.GetValueById("dev_name")
                    self.result['dev_model']=self.GetTextById("dev_model")
                    self.driver.switch_to.default_content()
                    
                if(li.text in self.title["TIMESETTING"]):
                    li.click()
                    print('        [时钟设置]:')
                    self.driver.find_element_by_id("homeFrame")	
                    self.driver.switch_to.frame("homeFrame")
                    print('时区 : ',self.GetFirstSelectedById("TimeZone"))
                    self.result['TimeZone']=self.GetFirstSelectedById("TimeZone")
                    if self.IsSelectedById("ntpserviceen"):
                        print('时钟同步开关 : ',"开")
                        self.result['ntpserviceen']='open'
                    else:
                        print('时钟同步开关 : ',"关")
                        self.result['ntpserviceen']='close'
                    self.driver.switch_to.default_content()
                if(li.text in self.title["SYSOPERA"]):
                    li.click()
                    self.driver.find_element_by_id("homeFrame")	
                    self.driver.switch_to.frame("homeFrame")
                    print('        [系统维护]:')
                    
                    if self.IsSelectedById("ckarb"):
                        print('自动重启 : ',"开")
                        self.result['ckarb']='open'
                    else:
                        self.result['ckarb']='close'
                        print('自动重启 : ',"关")
                    self.driver.switch_to.default_content()


        
    def test_netset(self):
        ul=self.model_init("sub2Span")
        for li in ul:
            if(len(li.text)>0):
                if(li.text in self.title["ETHNET"]):
                    li.click()
                    sleep(2)
                    self.driver.find_element_by_id("homeFrame")	
                    self.driver.switch_to.frame("homeFrame")
                    print('        [以太网]:')
                    print('IP地址: ',self.GetValueById("form_ip_octet_1")+'.'+self.GetValueById("form_ip_octet_2")+'.'+self.GetValueById("form_ip_octet_3")+'.'+self.GetValueById("form_ip_octet_4"))
                    self.result['ipAddress']=self.GetValueById("form_ip_octet_1")+'.'+self.GetValueById("form_ip_octet_2")+'.'+self.GetValueById("form_ip_octet_3")+'.'+self.GetValueById("form_ip_octet_4")
                    if(self.IsSelectedById("autoipSwitch")):
                        print('IP自适应: 开启')
                        self.result['autoipSwitch']='open'
                    else:
                        print('IP自适应: 关闭')
                        self.result['autoipSwitch']='close'
                    if(self.IsSelectedById("dhcpSwitch")):
                        print('dhcp    : 开启')
                        self.result['dhcpSwitch']='open'
                    else:
                        print('dpcp    : 关闭')
                        self.result['dhcpSwitch']='close'
                    self.driver.switch_to.default_content()
                elif(li.text in self.title["NETPORT"]):
                    li.click()
                    sleep(2)
                    self.driver.find_element_by_id("homeFrame")	
                    self.driver.switch_to.frame("homeFrame")
                    print('        [网络端口]:')
                    print('HTTP PORT: ',self.GetValueById("porthttp"))
                    print('RTSP PORT: ',self.GetValueById("portrtsp"))
                    self.result['porthttp']=self.GetValueById("porthttp")
                    self.result['portrtsp']=self.GetValueById("portrtsp")
                    self.driver.switch_to.default_content()
        
    def test_videoset(self):
        ul=self.model_init("sub3Span")
        for li in ul:
            if(len(li.text)>0):
                if(li.text in self.title["VIDEOSETTING"]):
                    li.click()
                    self.driver.find_element_by_id("homeFrame")	
                    self.driver.switch_to.frame("homeFrame")
                    sleep(1)
                    try:
                        WebDriverWait(self.driver,20,0.5).until(EC.presence_of_element_located((By.ID,"divColorParamSet")))
                    except:
                        pass
                    else:
                        print('        [图像设定]:')
                        self.MyClickById("divColorParamSet")#颜色参数
                        sleep(2)
                        self.result['image_effect_cfg']={}
                        print('亮度 : ',self.GetTextById("tdBright"))
                        print('对比度 : ',self.GetTextById("tdContrast"))
                        print('饱和度 : ',self.GetTextById("tdSaturation"))
                        print('锐度 : ',self.GetTextById("tdSharpness"))
                        print('夜视亮度 : ',self.GetTextById("tdNightluma"))
                        print('强光抑制 : ',self.GetTextById("tdHighLightSuppress"))
                        print('增益 : ',self.GetTextById("tdGain"))
                        print('宽动态 : ',self.GetTextById("tdWdr"))
                        self.result['image_effect_cfg']['Bright']=self.GetTextById("tdBright")
                        self.result['image_effect_cfg']['Contrast']=self.GetTextById("tdContrast")
                        self.result['image_effect_cfg']['Saturation']=self.GetTextById("tdSaturation")
                        self.result['image_effect_cfg']['Sharpness']=self.GetTextById("tdSharpness")
                        self.result['image_effect_cfg']['Nightluma']=self.GetTextById("tdNightluma")
                        self.result['image_effect_cfg']['HighLightSuppress']=self.GetTextById("tdHighLightSuppress")
                        self.result['image_effect_cfg']['Gain']=self.GetTextById("tdGain")
                        self.result['image_effect_cfg']['Wdr']=self.GetTextById("tdWdr")
                        if(self.driver.find_element_by_id("lampchkOpen").is_selected()):
                            print('光源频率 : ','50Hz')
                            self.result['image_effect_cfg']['Light_source_frequency']='50Hz'
                        else:
                            print('光源频率 : ','60Hz')
                            self.result['image_effect_cfg']['Light_source_frequency']='60Hz'
                    
                    
                        self.MyClickById("divVideoControl")#视频镜像
                        sleep(2)
                        
                        VideoControl=['正常',' 水平',' 垂直',' 对角']
                        for i in range(4):
                            if self.driver.find_elements_by_name("videoreverse")[i].is_selected():
                                print("镜像:",VideoControl[i])
                                self.result['image_effect_cfg']['videoreverse']=VideoControl[i]
                                break
                        
                        self.MyClickById("divAdvanceSet")#高级设置
                        sleep(2)
                        
                        print('电子快门:',self.GetFirstSelectedById("AESelect"))
                        print('白平衡:',self.GetFirstSelectedById("AWBSelect"))
                        self.result['image_effect_cfg']['AE']=self.GetFirstSelectedById("AESelect")
                        self.result['image_effect_cfg']['AWB']=self.GetFirstSelectedById("AWBSelect")
                        
                        print('红增益 : ',self.GetValueById("redgain"))
                        print('蓝增益 : ',self.GetValueById("blurgain"))
                        print('低照增强:',self.GetValueById("lowlightenhance"))
                        self.result['image_effect_cfg']['redgain']=self.GetValueById("redgain")
                        self.result['image_effect_cfg']['blurgain']=self.GetValueById("blurgain")
                        self.result['image_effect_cfg']['tdlowlightenhance']=self.GetValueById("lowlightenhance")
                        
                        print('曝光权重:',self.GetFirstSelectedById("aewinweight"))
                        print('人脸增强:',self.GetFirstSelectedById("nightfacemode"))
                        print('去雾增强 : ',self.GetValueById("strengthenToMist"))
                        self.result['image_effect_cfg']['StrengthenToMist']=self.GetValueById("strengthenToMist")
                        self.result['image_effect_cfg']['aewinweight']=self.GetFirstSelectedById("aewinweight")
                        self.result['image_effect_cfg']['nightfacemode']=self.GetFirstSelectedById("nightfacemode")
                        self.driver.switch_to.default_content()
                        self.model_init('sub3Span')
                elif(li.text in self.title["AUDIOSET"]):
                    li.click()
                    sleep(3)
                    self.driver.find_element_by_id("homeFrame")	
                    self.driver.switch_to.frame("homeFrame")
                    print('        [音频]:')
                    self.result['audio_cfg']={}
                    if(self.driver.find_elements_by_name("rdAudioIN")[0].is_selected()):
                        print('音频             : 开启')
                        print('音频输入音量     : '	  ,self.GetTextById("tdInvolume"))
                        print('音频输出音量     : '	  ,self.GetTextById("tdOutvolume"))
                        self.result['audio_cfg']['Audio']='open'
                        self.result['audio_cfg']['Involume']=self.GetTextById("tdInvolume")
                        self.result['audio_cfg']['Outvolume']=self.GetTextById("tdOutvolume")
                    else:
                        print('音频             : 关闭')
                        print('音频输入音量     : '	  ,self.GetTextById("divInvolume"))
                        print('音频输出音量     : '	  ,self.GetTextById("divOutvolume"))
                        self.result['audio_cfg']['Audio']='close'
                        self.result['audio_cfg']['Involume']=self.GetTextById("divInvolume")
                        self.result['audio_cfg']['Outvolume']=self.GetTextById("divOutvolume")
                    print('音频输入方式     : ',self.GetFirstSelectedById("inputtype"))
                    print('音频输入编码格式 : ',self.GetFirstSelectedById("codetype"))
                    self.result['audio_cfg']['inputtype']=self.GetFirstSelectedById("inputtype")
                    self.result['audio_cfg']['codetype']=self.GetFirstSelectedById("codetype")
                    self.driver.switch_to.default_content()
                elif(li.text in self.title["SUBTITLE_OVERLAY"]):
                    li.click()
                    self.driver.find_element_by_id("homeFrame")	
                    self.driver.switch_to.frame("homeFrame")
                    js='document.getElementById("divBasic").click()'
                    self.driver.execute_script(js)
                    sleep(2)
                    print('        [OSD]:')
                    self.result['osd_cfg']={}
                    if(self.IsSelectedById("name_enb")):
                        print('名称开关 : 开启')
                        self.result['osd_cfg']["name_enb"]='open'
                    else:
                        print('名称开关 : 关闭')
                        self.result['osd_cfg']["name_enb"]='close'
					
                    if(self.IsSelectedById("time_enb")):
                        print('时间开关 : 开启')
                        self.result['osd_cfg']["time_enb"]='open'
                    else:
                        print('时间开关 : 关闭')
                        self.result['osd_cfg']["time_enb"]='close'
					
                    if(self.IsSelectedById("osd_enb")):
                        print('osd开关  : 开启')
                        self.result['osd_cfg']["osd_enb"]='open'
                    else:
                        print('osd开关  : 关闭')
                        self.result['osd_cfg']["osd_enb"]='close'
					
                    if(self.IsSelectedById("bps_enb")):
                        print('码流     : 开启')
                        self.result['osd_cfg']["bps_enb"]='open'
                    else:
                        print('码流     : 关闭')
                        self.result['osd_cfg']["bps_enb"]='close'
					
                    print('名称     : ',self.GetValueById("name"))
                    print('OSD名称  : ',self.GetValueById("osdname"))
                    print('颜色     : ',self.GetFirstSelectedById("colorOption"))
                    print('字体大小 : ',self.GetFirstSelectedById("osd_font"))
                    self.result['osd_cfg']["name"]=self.GetValueById("name")
                    self.result['osd_cfg']["osdname"]=self.GetValueById("osdname")
                    self.result['osd_cfg']["colorOption"]=self.GetFirstSelectedById("colorOption")
                    self.result['osd_cfg']["osd_font"]=self.GetFirstSelectedById("osd_font")
                    self.result['osd_cfg']["osd_language"] = self.GetFirstSelectedById("osd_language")
                    r = requests.get("http://"+self.ip+'/?jcpcmd=osdcfg -act list',cookies=dict(loginflag='1'))
                    print(r.text.split(';')[1],r.text.split(';')[2])#time
                    print(r.text.split(';')[4],r.text.split(';')[5])#bps
                    print(r.text.split(';')[7],r.text.split(';')[8])#name
                    self.result['osd_cfg']["time_coordinate"] = r.text.split(';')[1]+';'+r.text.split(';')[2]
                    self.result['osd_cfg']["bps_coordinate"]  = r.text.split(';')[4]+';'+r.text.split(';')[5]
                    self.result['osd_cfg']["name_coordinate"] = r.text.split(';')[7]+';'+r.text.split(';')[8]
                    self.driver.switch_to.default_content()
                    self.model_init('sub3Span')
                elif(li.text in self.title["EXTEND_DISPOSE"]):
                    li.click()
                    sleep(2)
                    self.driver.find_element_by_id("homeFrame")	
                    self.driver.switch_to.frame("homeFrame")
                    print('        [3D数字降噪]:')
                    if self.IsSelectedById('denoise_open'):
                        print('降噪使能','开')
                        self.result["denoise"] = 'open'
                    if self.IsSelectedById('denoise_close'):
                        print('降噪使能','关')
                        self.result["denoise"] = 'close'
                    print('降噪强度',self.GetTextById('tdStrengthValue'))
                    self.result["StrengthValue"] = self.GetTextById('tdStrengthValue')
                    
                    print('        [NVR适配]:')
                    if(self.IsSelectedById("nvr_open")):
                        print('NVR适配:开启')
                        self.result["nvr_open"]='open'
                    else:
                        if(self.IsSelectedById("nvr_close")):
                            print('NVR适配:关闭')
                            self.result["nvr_open"]='close'
                        else:
                            print('EMPTY')
                            self.result["nvr_open"]='EMPTY'
                    self.driver.switch_to.default_content()
                elif(li.text in self.title["CHANNELSETTING"]):
                    li.click()
                    sleep(2)
                    self.driver.find_element_by_id("homeFrame")	
                    self.driver.switch_to.frame("homeFrame")
                    print('        [主码流]:')
                    self.result['stream_master_cfg']={}
                    print('分辨率     : ',self.GetFirstSelectedById("selStreamMaster"))
                    print('帧率       : ',self.GetValueById("frmrateMaster"))
                    print('码率       : ',self.GetValueById("bitrateMaster"))
                    print('I帧间隔    : ',self.GetValueById("frmintrMaster"))
                    print('码率控制   : ',self.GetFirstSelectedById("selRateCtrlMaster"))
                    print('压缩格式   : ',self.GetFirstSelectedById("selVeEncMaster"))
                    self.result['stream_master_cfg']["selStreamMaster"]=self.GetFirstSelectedById("selStreamMaster")
                    self.result['stream_master_cfg']["frmrateMaster"]=self.GetValueById("frmrateMaster")
                    self.result['stream_master_cfg']["bitrateMaster"]=self.GetValueById("bitrateMaster")
                    self.result['stream_master_cfg']["frmintrMaster"]=self.GetValueById("frmintrMaster")
                    self.result['stream_master_cfg']["selRateCtrlMaster"]=self.GetFirstSelectedById("selRateCtrlMaster")
                    self.result['stream_master_cfg']["selVeEncMaster"]=self.GetFirstSelectedById("selVeEncMaster")
                    print('        [从码流]:')
                    self.result['stream_slave_cfg']={}
                    print('分辨率     : ',self.GetFirstSelectedById("selStreamSlave"))
                    print('帧率       : ',self.GetValueById("frmrateSlave"))
                    print('码率       : ',self.GetValueById("bitrateSlave"))
                    print('I帧间隔    : ',self.GetValueById("frmintrSlave"))
                    print('码率控制   : ',self.GetFirstSelectedById("selRateCtrlSlave"))
                    print('压缩格式   : ',self.GetFirstSelectedById("selVeEncSlave"))
                    self.result['stream_slave_cfg']["selStreamSlave"]=self.GetFirstSelectedById("selStreamSlave")
                    self.result['stream_slave_cfg']["frmrateSlave"]=self.GetValueById("frmrateSlave")
                    self.result['stream_slave_cfg']["bitrateSlave"]=self.GetValueById("bitrateSlave")
                    self.result['stream_slave_cfg']["frmintrSlave"]=self.GetValueById("frmintrSlave")
                    self.result['stream_slave_cfg']["selRateCtrlSlave"]=self.GetFirstSelectedById("selRateCtrlSlave")
                    self.result['stream_slave_cfg']["selVeEncSlave"]=self.GetFirstSelectedById("selVeEncSlave")
                    self.driver.switch_to.default_content()
                
                elif(li.text in self.title["FILL_LIGHT_SETTING"]):
                    li.click()
                    sleep(2)
                    self.driver.find_element_by_id("homeFrame")	
                    self.driver.switch_to.frame("homeFrame")
                    print('        [补光设置]:')
                    self.result['fill_light_cfg']={}
                    
                    if self.IsDisplayById('tr_variable_optical') == -1: # 调光使能
                        pass
                    else:
                        if self.IsDisplayById('tr_variable_optical'):

                            if self.IsSelectedById("optical_open"):
                                print('调光使能   : 开启')
                                self.result['fill_light_cfg']["optical_open"]='open'
                            if self.IsSelectedById("optical_close"):
                                print('调光使能   : 关闭')
                                self.result['fill_light_cfg']["optical_open"]='close'

                    print('设备类型     : ',self.GetFirstSelectedById("switchdevtype"))
                    self.result['fill_light_cfg']["switchdevtype"]=self.GetFirstSelectedById("switchdevtype")

                    print('开启模式     : ',self.GetFirstSelectedById("switchmode"))
                    self.result['fill_light_cfg']["switchmode"]=self.GetFirstSelectedById("switchmode")

                    if self.IsDisplayById('tr_control_mode') == -1: # 控制模式
                        pass
                    else:
                        if self.IsDisplayById('tr_control_mode'):
                            print('控制模式 : ', self.GetFirstSelectedById("switchctrlmode"))
                            self.result['fill_light_cfg']["switchctrlmode"] = self.GetFirstSelectedById("switchctrlmode")
                    
                    if self.IsDisplayById('tr_open_light_sensitivity') == -1: # 开灯灵敏度
                        pass
                    else:
                        if self.IsDisplayById('tr_open_light_sensitivity'):
                            print('开灯灵敏度 : ', self.GetTextById("tdSensitivity_open"))
                            print('开灯灵敏度 : ', self.GetTextById("tdSensitivity_close"))
                            self.result['fill_light_cfg']["tdSensitivity_open"] = self.GetTextById("tdSensitivity_open")
                            self.result['fill_light_cfg']["tdSensitivity_close"]=self.GetTextById("tdSensitivity_close")
                    
                    if self.IsDisplayById('tr_shine_1') == -1: # 闪灯模式
                        pass
                    else:
                        if self.IsDisplayById('tr_shine_1'):
                            print('闪灯模式 : ', self.GetFirstSelectedById("shinemode"))
                            self.result['fill_light_cfg']["shinemode"] = self.GetFirstSelectedById("shinemode")
                    
                    if self.IsDisplayById('tr_shine_2') == -1: # 闪灯时间
                        pass
                    else:
                        if self.IsDisplayById('tr_shine_2'):
                            js = "return document.getElementById('shinetime').value"
                            res = self.driver.execute_script(js)
                            self.result['fill_light_cfg']["shinetime"] = res
                            print('闪灯时间 : ', self.result['fill_light_cfg']["shinetime"])
                    
                    if self.IsDisplayById('tr_shine_3') == -1: # 白光灯控制
                        pass
                    else:
                        if self.IsDisplayById('tr_shine_3'):
                            print('白光灯控制 : ', self.GetFirstSelectedById("white_reverse"))
                            self.result['fill_light_cfg']["white_reverse"] = self.GetFirstSelectedById("white_reverse")

                    if self.IsDisplayById('irledctrl') == -1: # 红外灯控制
                        pass
                    else:
                        if self.IsDisplayById('irledctrl'):
                            print('红外灯控制 : ', self.GetFirstSelectedById("irled_reverse"))
                            self.result['fill_light_cfg']["irled_reverse"] = self.GetFirstSelectedById("irled_reverse")

                    if self.IsDisplayById('tr_time_of_night') == -1: # 夜间时间
                        pass
                    else:
                        if self.IsDisplayById('tr_time_of_night'):
                            self.result['fill_light_cfg']["night_time"] = self.GetFirstSelectedById("night_time1")+':'+self.GetFirstSelectedById("night_time2")+'-'+self.GetFirstSelectedById("night_time3")+':'+self.GetFirstSelectedById("night_time4")
                            print('夜间时间 : ', self.result['fill_light_cfg']["night_time"])

                    if self.IsDisplayById('tr_light_supperssion') == -1: # 发蒙抑制
                        pass
                    else:
                        if self.IsDisplayById('tr_light_supperssion'):
                            if self.IsSelectedById('light_supperssion_open'):
                                print('发蒙抑制 : 开启')
                                self.result['fill_light_cfg']["light_supperssion"] = 'open'
                            if self.IsSelectedById('light_supperssion_close'):
                                print('发蒙抑制 : 关闭')
                                self.result['fill_light_cfg']["light_supperssion"] = 'close'
                    self.driver.switch_to.default_content()
                
                elif(li.text in self.title["INFRARED_SETTING"]):
                    li.click()
                    sleep(2)
                    self.result['infrared_cfg']={}
                    self.driver.find_element_by_id("homeFrame")	
                    self.driver.switch_to.frame("homeFrame")
                    print('        [红外设置]:')
                    print('模式       : ',self.GetFirstSelectedById("switchmode"))
                    self.result['infrared_cfg']["switchmode"]=self.GetFirstSelectedById("switchmode")
                    print('夜间时间   : ',self.GetFirstSelectedById("night_time1")+':'+self.GetFirstSelectedById("night_time2")+'-'+self.GetFirstSelectedById("night_time3")+':'+self.GetFirstSelectedById("night_time4"))
                    self.result['infrared_cfg']["night_time"]=self.GetFirstSelectedById("night_time1")+':'+self.GetFirstSelectedById("night_time2")+'-'+self.GetFirstSelectedById("night_time3")+':'+self.GetFirstSelectedById("night_time4")
                    print('灵敏度     : ',self.GetTextById("tdSensitivity"))
                    self.result['infrared_cfg']["tdSensitivity"]=self.GetTextById("tdSensitivity")
                    self.driver.switch_to.default_content()
                    

                elif(li.text in self.title["IRCUT_SETTING"]):
                    li.click()
                    sleep(2)
                    self.driver.find_element_by_id("homeFrame")	
                    self.driver.switch_to.frame("homeFrame")
                    print('        [IRCUT设置]:')
                    print('IRCUT模式  : ',self.GetFirstSelectedById("ircut_mode"))
                    self.result["ircut_mode"]=self.GetFirstSelectedById("ircut_mode")
                    self.driver.switch_to.default_content()
                else:
                    pass
    
    def get_alarm_cfg(self,model):
        if model=='motion':
            url='http://'+self.IP+'/?jcpcmd=mdmbcfg -act list'
        elif model=='cross':
            url='http://'+self.IP+'/?jcpcmd=vgline -act list'
        elif model=='area':
            url='http://'+self.IP+'/?jcpcmd=vgrect -act list'
        elif model=='vl':
            url='http://'+self.IP+'/?jcpcmd=vlcfg -act list'
        elif model=='vm':
            url='http://'+self.IP+'/?jcpcmd=vmaskalarmcfg -act list'
        
        r=requests.get(url,cookies={'loginflag':'1'})
        res=r.text
        res=re.sub('["\r\n]','',res).split('szJcpResult=[Success]')[1].split(';')
        data={}
        for i in res:
            if len(i)>0:
                data[i.split('=')[0]]=i.split('=')[1]
        return data
    
    def test_alarmset(self):
        ul=self.model_init("sub5Span")
        for li in ul:
            if(len(li.text)>0):
                li.click()
                print("["+li.text+"]")
                sleep(1)
                li.click()
                if(li.text in self.title["MENU_MOTION"]):#移动侦测
                    self.driver.find_element_by_id("homeFrame")	
                    self.driver.switch_to.frame("homeFrame")
                    self.result['motion_cfg']={}
                    if(self.IsSelectedById("motion_enb")):
                        print(' 移动侦测   : 开启')
                        self.result['motion_cfg']['enable']='open'
                    else:
                        self.result['motion_cfg']['enable']='close'
                        print(' 移动侦测   : 关闭')
                    print(" 移动侦测灵敏度:",self.GetTextById("m_slider_span"))
                    self.result['motion_cfg']['m_slider']=self.GetTextById("m_slider_span")
                    data=self.get_alarm_cfg('motion')
                    print(data['mbdesc'])
                    self.result['motion_cfg']['mbdesc']=data['mbdesc']
                    print(data['timestrategy'])
                    self.result['motion_cfg']['timestrategy']=data['timestrategy']
                    self.driver.switch_to.default_content()
                if(li.text in self.title["monitor_cross_alarm"]):#越界
                    self.result['vgline_cfg']={}
                    self.driver.find_element_by_id("homeFrame")	
                    self.driver.switch_to.frame("homeFrame")
                    if self.IsSelectedById('cross_monitor_enb'):
                        print(' 越界侦测   : 开启')
                        self.result['vgline_cfg']['enable']='open'
                    else:
                        print(' 越界侦测   : 关闭')
                        self.result['vgline_cfg']['enable']='close'
                    if self.IsSelectedById('cross_blink_enb'):
                        print(' 越界闪烁   : 开启')
                        self.result['vgline_cfg']['cross_blink_enb']='open'
                    else:
                        print(' 越界闪烁   : 关闭')
                        self.result['vgline_cfg']['cross_blink_enb']='close'
                    print(' 场景模式 : ',self.GetFirstSelectedById('select_cross_scene_mode'))#模式
                    print(' 方向 : ',self.GetFirstSelectedById('select_cross_direction'))#方向
                    print(' 越界侦测灵敏度 : ',self.GetTextById('m_slider_span_cross_monitor'))#灵敏度
                    data=self.get_alarm_cfg('cross')
                    print(data['timestrategy'])
                    self.result['vgline_cfg']['cross_scene_mode']=self.GetFirstSelectedById('select_cross_scene_mode')
                    self.result['vgline_cfg']['cross_direction']=self.GetFirstSelectedById('select_cross_direction')
                    self.result['vgline_cfg']['cross_monitor']=self.GetTextById('m_slider_span_cross_monitor')
                    self.result['vgline_cfg']['timestrategy']=data['timestrategy']
                    self.result['vgline_cfg']['x0']=data['x0']
                    self.result['vgline_cfg']['y0']=data['y0']
                    self.result['vgline_cfg']['x1']=data['x1']
                    self.result['vgline_cfg']['y1']=data['y1']
                    self.result['vgline_cfg']['dx0']=data['dx0']
                    self.result['vgline_cfg']['dy0']=data['dy0']
                    self.result['vgline_cfg']['dx1']=data['dx1']
                    self.result['vgline_cfg']['dy1']=data['dy1']
                    self.driver.switch_to.default_content()
                if(li.text in self.title["monitor_area_alarm"]):#区域
                    self.driver.find_element_by_id("homeFrame")	
                    self.driver.switch_to.frame("homeFrame")
                    self.result['vgrect_cfg']={}
                    if self.IsSelectedById('area_monitor_enb'):
                        print(' 区域侦测   : 开启')
                        self.result['vgrect_cfg']['enable']='open'
                    else:
                        print(' 区域侦测   : 关闭')
                        self.result['vgrect_cfg']['enable']='close'
                    if self.IsSelectedById('area_blink_enb'):
                        print(' 区域闪烁   : 开启')
                        self.result['vgrect_cfg']['blink_enb']='open'
                    else:
                        print(' 区域闪烁   : 关闭')
                        self.result['vgrect_cfg']['blink_enb']='close'
                    print(" 场景模式 : "+self.GetFirstSelectedById('select_area_scene_mode'))#模式
                    print(" 方向 : "+self.GetFirstSelectedById('select_area_direction'))#方向
                    print(" 区域侦测灵敏度 : "+self.GetTextById('m_slider_span_area_monitor'))#灵敏度

                    data=self.get_alarm_cfg('area')
                    print(data['timestrategy'])
                    self.result['vgrect_cfg']['area_scene_mode']=self.GetFirstSelectedById('select_area_scene_mode')
                    self.result['vgrect_cfg']['area_direction']=self.GetFirstSelectedById('select_area_direction')
                    self.result['vgrect_cfg']['area_monitor']=self.GetTextById('m_slider_span_area_monitor')
                    self.result['vgrect_cfg']['timestrategy']=data['timestrategy']
                    self.result['vgrect_cfg']['x0']=data['x0']
                    self.result['vgrect_cfg']['x1']=data['x1']
                    self.result['vgrect_cfg']['x2']=data['x2']
                    self.result['vgrect_cfg']['x3']=data['x3']
                    self.result['vgrect_cfg']['y0']=data['y0']
                    self.result['vgrect_cfg']['y1']=data['y1']
                    self.result['vgrect_cfg']['y2']=data['y2']
                    self.result['vgrect_cfg']['y3']=data['y3']
                    self.driver.switch_to.default_content()
                if(li.text in self.title["VL_TIME_STRATEGY"]):#视频丢失
                    self.driver.find_element_by_id("homeFrame")	
                    self.driver.switch_to.frame("homeFrame")
                    self.result['vl_cfg']={}
                    if self.IsSelectedById('losschk'):
                        print(' 视频丢失   : 开启')
                        self.result['vl_cfg']['enable']='open'
                    else:
                        print(' 视频丢失   : 关闭')
                        self.result['vl_cfg']['enable']='close'                        
                    data=self.get_alarm_cfg('vl')
                    print(data['timestrategy'])
                    self.result['vl_cfg']['timestrategy']=data['timestrategy']
                    self.driver.switch_to.default_content()
                if(li.text in self.title["VM_TIME_STRATEGY"]):#视频遮挡
                    self.driver.find_element_by_id("homeFrame")	
                    self.driver.switch_to.frame("homeFrame")
                    self.result['vm_cfg']={}
                    if self.IsSelectedById('vmchk'):
                        print(' 视频遮挡   : 开启')
                        self.result['vm_cfg']['enable']='open'
                    else:
                        print(' 视频遮挡   : 关闭')
                        self.result['vm_cfg']['enable']='close'
                    print(" 视频遮挡报警灵敏度 : "+self.GetTextById('tdVmtype'))#灵敏度
                    data=self.get_alarm_cfg('vm')
                    print(data['timestrategy'])
                    self.result['vm_cfg']['tdVmtype']=self.GetTextById('tdVmtype')
                    self.result['vm_cfg']['timestrategy']=data['timestrategy']
                    self.driver.switch_to.default_content()
                if(li.text in self.title["ALARMLINKAGE"]):#报警联动
                    self.driver.find_element_by_id("homeFrame")	
                    self.driver.switch_to.frame("homeFrame")
                    email_id=['cbMDEmail','cbVGLineEmail','cbVGRectEmail','cbVLEmail','cbVMEmail','cbDEEmail']
                    voice_id=['cbMDAudio','cbVGLineAudio','cbVGRectAudio']
                    email_type={
                        'cbMDEmail':'移动侦测邮件联动',
                        'cbVGLineEmail':'越界侦测邮件联动',
                        'cbVGRectEmail':'区域侦测邮件联动',
                        'cbVLEmail':'视频丢失邮件联动',
                        'cbVMEmail':'视频遮挡邮件联动',
                        'cbDEEmail':'磁盘错误邮件联动'
                    }
                    voice_type={
                        'cbMDAudio':'移动侦测音频联动',
                        'cbVGLineAudio':'越界侦测音频联动',
                        'cbVGRectAudio':'区域侦测音频联动'
                    }
                    self.result['email_link']={}
                    self.result['audio_link']={}
                    for id in email_id:
                        if self.IsSelectedById(id) == -1:
                            pass
                        else:
                            if self.IsSelectedById(id):
                                self.result['email_link'][id]='open'
                                print(" "+email_type[id],' : 开启')
                            else:
                                self.result['email_link'][id]='close'
                                print(" "+email_type[id],' : 关闭')
                    for id in voice_id:
                        if self.IsSelectedById(id) == -1:
                            pass
                        else:
                            if self.IsSelectedById(id):
                                self.result['audio_link'][id]='open'
                                print(" "+voice_type[id],' : 开启')
                            else:
                                self.result['audio_link'][id]='close'
                                print(" "+voice_type[id],' : 关闭')
                    self.driver.switch_to.default_content()
    def test_localset(self):
        pass
	
    def test_platset(self):
        ul = self.model_init("sub7Span")
        print('        [平台设置]:')
        if ul == 'EMPTY':
            print('EMPTY')
        else:
            for li in ul:
                if(len(li.text)>0):
                    if(li.text in self.title["DANALE_PLATFORM"]):
                        li.click()
                        sleep(1)
                        self.driver.find_element_by_id("homeFrame")	
                        self.driver.switch_to.frame("homeFrame")
                        
                        '''
                        try:
                            dana = self.driver.find_elements_by_name("danale_switch")
                            ali = False
                            print("find dana")
                            print(dana)
                        except:
                            print("cant't find danale")
                            ali = self.driver.find_elements_by_name("aliyun_switch")
                            dana = False
                        '''
                        
                        dana = self.driver.find_elements_by_name("danale_switch")
                        ali = False
                        if len(dana) == 0:
                            ali = self.driver.find_elements_by_name("aliyun_switch")
                            dana = False
                        
                        if dana:
                            if(dana[0].is_selected()):
                                print('大拿: 开启')
                                self.result["danale_switch"]='open'
                            else:
                                print('大拿: 关闭')
                                self.result["danale_switch"]='close'
                        if ali:
                            if(ali[0].is_selected()):
                                print('ali: 开启')
                                self.result["aliyun_switch"]='open'
                            else:
                                print('ali: 关闭')
                                self.result["aliyun_switch"]='close'
                        sleep(2)
                        self.driver.switch_to.default_content()
                    if(li.text in self.title["GUOB"]):
                        li.click()
                        sleep(1)
                        self.driver.find_element_by_id("homeFrame")	
                        self.driver.switch_to.frame("homeFrame")
                        dana=self.driver.find_elements_by_name("guobiao_switch")
                        if(dana[0].is_selected()):
                            print('国标: 开启')
                            self.result["guobiao_switch"]='open'
                        else:
                            print('国标: 关闭')
                            self.result["guobiao_switch"]='close'
                        sleep(2)
                        self.driver.switch_to.default_content()


    def test_hb_platset(self):
        ul=self.model_init("sub8Span")
        print('        [汉邦平台设置]:')
        # print(1111111111111111111111111,ul)
        if type(ul) == str:
            raise Exception('not found element')
        for li in ul:
            li.click()
            sleep(1)
            self.driver.find_element_by_id("homeFrame")	
            self.driver.switch_to.frame("homeFrame")

            hb=self.driver.find_elements_by_name("enable")

            if(hb[0].is_selected()):
                print('汉邦平台: 开启')
                self.result["hb_enable"]='open'
            else:
                print('汉邦平台: 关闭')
                self.result["hb_enable"]='close'
            print('端口号：',self.GetValueById('port'))
            print('注册码：',self.GetValueById('dev_id'))
            print('服务器地址：',self.GetValueById('serverip'))
            self.result["hb_server_port"]=self.GetValueById('port')
            self.result["hb_server_id"]=self.GetValueById('dev_id')
            self.result["hb_server_ip"]=self.GetValueById('serverip')
            self.driver.switch_to.default_content()
        
                        
    def match_version(self):
        print(self.version)
   
    def get_filepath_from_version_old(self):
        res=re.findall('^((?:V[BDT]?|T[BD]?|Z[BDT]?|W[T]?|VCF?))A?(\d)\.(\d*\w*)\.\d{4}-\d{8}-(?:HDXP2P|HDXGP2P|XMP2P|DANALE|NORMAL|WIFI|HBP2P)-(.*?)$',self.version)
        if res != None:
            version_type = res[0][0]
            cpu_type	 = str(res[0][1])
            sensor_type  = res[0][2]
            custom_type  = res[0][3]
            if cpu_type=='2':
                if sensor_type[0]=='2' or sensor_type=='33' or sensor_type=='35':
                    dirname='313'
                elif sensor_type[0]=='1':
                    dirname='T21'
                    cpu_type='1'
                else:
                    dirname='316'
            elif cpu_type=='1':
                if sensor_type[0]=='8':
                    cpu_type='2'
                    dirname='328'
                else:
                    dirname='T20'
            elif cpu_type=='3':
                dirname='uclibc'
            file="result/"+cpu_type+'/'+dirname+'/'+custom_type+'/'+version_type+'/'+sensor_type+'.txt'
            file1="result/"+cpu_type+'/'+dirname+'/'+custom_type+'/'+version_type+'/'
            return [file,file1,sensor_type]
        else:
            return False
    
    
    def my_test(self):
        self.match_result()
     
