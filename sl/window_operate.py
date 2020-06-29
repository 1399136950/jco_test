import autopy
from time import sleep
import win32api
import win32con
import ctypes
import win32gui
from random import randint
import cv2
from PIL import Image,ImageGrab
import numpy as np
import json
import os

from key import Key


class Operate:

    def __init__(self, wdname): 
        self.wdname = wdname
        self.hwnd = win32gui.FindWindow(None, self.wdname)

    def faker_move_mouse(self,x,y):
        autopy.mouse.move(x, y)

    def faker_click(self):
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN , 0,0,0,0)
        #sleep(0.02)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0,0,0,0)
        #sleep(0.02)
        # self.faker_move_mouse(self.x, self.y)
    
    def faker_click_right(self):
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN , 0,0,0,0)
        #sleep(0.02)
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0,0,0,0)
        #sleep(0.02)
        # self.faker_move_mouse(self.x, self.y)
    
    def find_tmp(self, srcImage, tmp_img_path='mouse.png'): # 找到与模板匹配的坐标
        templateImage = cv2.imread(tmp_img_path, 1)
        h, w = templateImage.shape[:2]  # rows->h, cols->w
        res = cv2.matchTemplate(srcImage, templateImage, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        print (max_val)
        left_top = max_loc  # 左上角
        if max_val < 0.5:
            return None,None
        right_bottom = (left_top[0] + w, left_top[1] + h)  # 右下角
        return left_top,right_bottom # 返回匹配的左上角坐标
            
    def move_to_window_coordinate(self, x, y): # x,y为相对窗口的坐标
        win32gui.SetForegroundWindow(self.hwnd)
        a,b,c,d = win32gui.GetWindowRect(self.hwnd)
        self.faker_move_mouse(a+x,b+y)

        
    def opposite_move(self, x, y): # 相对当前鼠标坐标来移动
        now_x,now_y = win32api.GetCursorPos()
        dst_x,dst_y = now_x+x, now_y+y
        self.faker_move_mouse(dst_x,dst_y)
        
    def screenShot(self): # 截取游戏图片
        
        win32gui.SetForegroundWindow(self.hwnd)
        win32gui.GetActiveWindow()
        x1,y1,x2,y2 = win32gui.GetWindowRect(self.hwnd) #
        print(x1,y1,x2,y2)
        self.faker_move_mouse(x2,y2)
        img_rgb = np.array(ImageGrab.grab((x1,y1,x2,y2))) #
        img_bgr = cv2.cvtColor(img_rgb,cv2.COLOR_RGB2BGR) # rgb to bgr
        return img_bgr
    
    def change_window(self, wdname):
        self.wdname = wdname
        self.hwnd = win32gui.FindWindow(None, self.wdname)
    
    def screenShot_th(self): # 截取游戏图片
        win32gui.SetForegroundWindow(self.hwnd)
        x1,y1,x2,y2 = win32gui.GetWindowRect(self.hwnd) #
        self.faker_move_mouse(x1,y1)
        img_rgb = np.array(ImageGrab.grab((x1,y1,x2,y2))) #
        img_bgr = cv2.cvtColor(img_rgb,cv2.COLOR_RGB2BGR) # rgb to bgr
        img_gay = cv2.cvtColor(img_rgb,cv2.COLOR_RGB2GRAY) # 灰阶图像
        _, img_th = cv2.threshold(img_gay,170,255,cv2.THRESH_BINARY)
        # cv2.imshow('', img_th)
        print('screenShot')
        return img_th
    

    
 
    
if __name__ == '__main__':
    p = Operate('sl')
    img = p.screenShot()
    cv2.imshow('', img)
    cv2.waitKey(0)
    p.change_window('python')
    img = p.screenShot()
    cv2.imshow('', img)
    cv2.waitKey(0)
