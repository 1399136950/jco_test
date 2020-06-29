import unittest
import requests
import re
import sys
from testcase import MyTest
from testcase_wlx import WlxTest
from testcase_hb import HbTest
import os

from mytelnet import MyTelnet


if __name__ == '__main__':
    print(os.popen('taskkill /F /IM iexplore.exe').read())
    suite = unittest.TestSuite()
    IP = input('请输入IP地址:')
    if re.findall('^\d+\.\d+\.\d+\.\d+$',IP):
        pass
    else:
        print('IP格式错误!')
        sys.exit()

    try:
        r = requests.get('http://'+IP+'/?jcpcmd=version -act list',cookies=dict(loginflag='1'),timeout=3)
    except:
        print('连接设备失败,请确认网络')
    else:
        try:
            tnl = MyTelnet(IP, 24)
        except:
            raise Exception('telnet port 24 err')

        try:
            version = re.findall('serverver=(.*?);', r.text)[0]
        except:
            print('无法获取版本')
        else:
            if re.findall('WLX',version):   # 威立信网页
                WlxTest.IP = IP
                WlxTest.index = 1
                tests = [
                    WlxTest("test_sysset"),
                    WlxTest("test_netset"),
                    WlxTest("test_videoparam"),
                    WlxTest("test_videoimage"),
                    WlxTest("test_alarmset"),
                    WlxTest("test_platset"),
                    WlxTest("end_test"),
                    WlxTest("match_result")
                ]

            elif re.findall('HB',version) or re.findall('FKS',version):     # 汉邦网页
                HbTest.IP = IP
                tests = [
                    HbTest("test_sysset"), 
                    HbTest("test_netset"), 
                    HbTest("test_videoset"), 
                    HbTest("test_alarmset"), 
                    HbTest("test_platset"), 
                    HbTest("test_hb_platset"), 
                    HbTest("end_test"), 
                    HbTest("match_result")
                ]

            else:   # 中性网页
                MyTest.IP = IP
                tests = [
                    MyTest("test_sysset"),
                    MyTest("test_netset"),
                    MyTest("test_videoset"),
                    MyTest("test_alarmset"),
                    MyTest("test_platset"),
                    MyTest("end_test"),
                    MyTest("match_result")
                ]
                
            suite.addTests(tests)
            runner = unittest.TextTestRunner()
            runner.run(suite)
        
	
