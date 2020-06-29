import unittest
import requests
import json
import re
import os
import sys
from socket import *
from selenium import webdriver
from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC


class NvrUpgrade:
    # 升级包路径,可随意添加修改
    update_file=[
        'E:\\myPHPScripts\\test\\nvr_upgrade\\upgrade_file\\MSR620D.base-C9-A.normal.20181017.nvr.tgz',
        'E:\\myPHPScripts\\test\\nvr_upgrade\\upgrade_file\\MSR620D.base-C9-A.normal.20181017.nvr.tgz'
    ]
    def upgrade(self):
        IP=input('ip:')
        driver=webdriver.Ie()
        driver.maximize_window()
        index=1
        while True:
            driver.get('http://'+IP)
            sleep(2)
            driver.find_element_by_id("loginuserName").clear()
            driver.find_element_by_id("loginuserName").send_keys("admin")
            
            driver.find_element_by_id("log_login").click()
            sleep(3)
            driver.find_element_by_id("setPage").click()
            sleep(1)
            driver.find_element_by_id("span-set").click()
            sleep(2)
            driver.switch_to.frame("paramSettingFrame")
            driver.find_element_by_id("menu5").click()
            sleep(1)
            driver.find_element_by_id("sub5Span").click()
            sleep(1)
            driver.find_element_by_id("sub5_4").click()
            sleep(1)
            driver.find_element_by_id("sub5_4Span").click()
            sleep(2)
            driver.switch_to.frame("paramSettingFrame")
            js='document.getElementById("filepathtmp").removeAttribute("readOnly")'
            driver.execute_script(js)
            js='document.getElementById("filepathtmp").removeAttribute("disabled")'
            driver.execute_script(js)
            num=index%len(self.update_file)
            driver.find_element_by_id("filepathtmp").send_keys(self.update_file[num])
            driver.find_element_by_id("btnUpgrade").click()
            sleep(1)
            print("NO.{},file is {}".format(index,self.update_file[num]))
            try:
                a = driver.switch_to.alert
            except:
                pass
            else:
                a.accept()
                sleep(20)
                self.is_update(IP)
                sleep(40)
                version=self.get_version(IP)
                if version:
                    print("success,version is {}".format(version))
                else:
                    print("can't get version info")
            index+=1
                   
    def get_version(self,IP):
        tcpSocket=socket(AF_INET, SOCK_STREAM)
        addr=(IP,9999)
        tcpSocket.settimeout(2)#设置超时
        try:
            tcpSocket.connect(addr)
        except:
            print("can't connect host",end="\n")
            return False
        else:
            tcpSocket.send("device_info -act list".encode())
            try:
                data=tcpSocket.recv(65535)
            except:
                tcpSocket.close()
                return False
            else:
                tcpSocket.close()
                return str(data).split(';')[-2]
    
    def get_progess(self,IP):
        tcpSocket = socket(AF_INET, SOCK_STREAM)
        addr=(IP, 9999)
        tcpSocket.settimeout(2)#设置超时
        try:
            tcpSocket.connect(addr)
        except:
            print("can't connect host",end="\n")
            return False
        else:
            tcpSocket.send("update -act list".encode())
            try:
                data=tcpSocket.recv(65535)
            except:
                tcpSocket.close()
                print('recv err',end="\n")
            else:
                tcpSocket.close()
                return int(str(data).split(';')[0].split('=')[1])
                
    def is_update(self,IP):
        progess=self.get_progess(IP)
        if progess:
            if progess>=0 and progess<100:
                print(progess,end="\r")
                sleep(2)
                self.is_update(IP)
            elif progess==100:
                print('success',end="\n")
            else:
                print('err')
        else:
            print("device is reboot",end="\n")
            
                 
a=NvrUpgrade()    
a.upgrade()


