from selenium import webdriver
from time import sleep
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from PIL import Image,ImageGrab
import numpy as np
import cv2

import win32gui

def get_index_from_screen(driver, tmpfile):
    pass

def screenShot(x1,y1,x2,y2): # 截取游戏图片
    
    # win32gui.SetForegroundWindow(self.hwnd)
    # win32gui.GetActiveWindow()
    # x1,y1,x2,y2 = win32gui.GetWindowRect(self.hwnd) #
    print(x1,y1,x2,y2)
    # self.faker_move_mouse(x2,y2)
    img_rgb = np.array(ImageGrab.grab((x1,y1,x2,y2))) #
    img_bgr = cv2.cvtColor(img_rgb,cv2.COLOR_RGB2BGR) # rgb to bgr
    return img_bgr

driver = webdriver.Chrome()
# driver.set_window_size(800,600)
driver.maximize_window()
driver.get('https://account.aliyun.com/login/login.htm?qrCodeFirst=false&oauth_callback=https%3A%2F%2Fliving.aliyun.com%2F')
'''
driver.switch_to.frame('alibaba-login-box')
driver.find_element_by_id('fm-login-id').send_keys('xujun19940828')
driver.find_element_by_id('fm-login-password').send_keys('XuJuN19940828')
'''
window_info = driver.get_window_rect()
x1,y1 = driver.get_window_position()['x'],driver.get_window_position()['y']
x2,y2 = x1+window_info['width'], y1+window_info['height']

screen_shot = screenShot(x1,y1,x2,y2)

with open('test.png', 'wb') as fd:
    fd.write(screen_shot)


