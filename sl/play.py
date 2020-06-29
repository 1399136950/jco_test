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
from key import Key
import json
import os


class SL:

    def __init__(self, model='low'): 
        self.wdname = '扫雷'
        self.hwnd = win32gui.FindWindow(None, self.wdname)

        if self.hwnd == 0:
            raise Exception("请打开扫雷软件")
        self.key = Key()
        shot_img = self.screenShot()
        
        
        # maps = shot_img[101:245,15:159]
        # cv2.imwrite('map_low.png',maps)
        
        self.init_game_mode(shot_img) # 初始化游戏模式
        self.pixel_len = 16
        self.m_count = 0
    
    
    def init_game_mode(self, shot_img):
        if abs(shot_img.shape[1] - 170) < 10:
            try:
                l,r = self.find_tmp(shot_img, 'map_low.png')
                self.x, self.y = l[0],l[1]
            except:
                pass
            else:
                self.maps = [ [None  for i in range(9)] for j in range(9)]
                self.all_mine_count = 10
                self.grid_line = 9
                self.grid_column = 9
                self.model = 'low'
        elif abs(shot_img.shape[1] - 282) < 10:
            try:
                l,r = self.find_tmp(shot_img, 'map_normal.png')
                self.x, self.y = l[0],l[1]
            except:
                pass
            else:
                self.maps = [ [None  for i in range(16)] for j in range(16)]
                self.all_mine_count = 40
                self.grid_line = 16
                self.grid_column = 16
                self.model = 'normal'
        elif abs(shot_img.shape[1] - 506) < 10:
            try:
                l,r = self.find_tmp(shot_img, 'map_hight.png')
                self.x, self.y = l[0],l[1]
            except:
                pass
            else:
                self.maps = [ [None  for i in range(30)] for j in range(16)]
                self.all_mine_count = 99
                self.grid_line = 16
                self.grid_column = 30
                self.model = 'hight'
        else:
            try:
                l,r = self.find_tmp(shot_img, 'map_hight1.png')
                self.x, self.y = l[0],l[1]
            except:
                pass
            else:
                self.maps = [ [None  for i in range(30)] for j in range(24)]
                self.all_mine_count = 99
                self.grid_line = 24
                self.grid_column = 30
                self.model = 'hight1'


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

    def move_to_window_grid(self,line,column): # x,y为相对窗口的坐标
        x = self.x + 7
        y = self.y + 7
        self.move_to_window_coordinate(x+16*column, y+16*line)
        
    def opposite_move(self, x, y): # 相对当前鼠标坐标来移动
        now_x,now_y = win32api.GetCursorPos()
        dst_x,dst_y = now_x+x, now_y+y
        self.faker_move_mouse(dst_x,dst_y)
        
    def screenShot(self): # 截取游戏图片
        win32gui.SetForegroundWindow(self.hwnd)
        x1,y1,x2,y2 = win32gui.GetWindowRect(self.hwnd) #
        self.faker_move_mouse(x1,y1)
        img_rgb = np.array(ImageGrab.grab((x1,y1,x2,y2))) #
        img_bgr = cv2.cvtColor(img_rgb,cv2.COLOR_RGB2BGR) # rgb to bgr
        return img_bgr
    
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
    

    def analysis_chessboard_ml(self):
        img = self.screenShot()
        img_gay = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY) # 灰阶图像
        _, img_th = cv2.threshold(img_gay,170,255,cv2.THRESH_BINARY)
        if self.model == 'low':
            maps = img_th[101:245,15:159]
        elif self.model == 'normal':
            maps = img_th[101:357,15:271]
        elif self.model == 'hight':
            maps = img_th[101:357, 15:495]
        
        for i in range(self.grid_line):
            for j in range(self.grid_column):
                l_s = i * self.pixel_len
                l_e = i * self.pixel_len + self.pixel_len
                c_s = j * self.pixel_len
                c_e = j * self.pixel_len + self.pixel_len
                res = self.train(maps[l_s:l_e, c_s:c_e])
                self.maps[i][j]=res
                if res == 'unknow':
                    self.unknow_count += 1
                
    def analysis_chessboard(self):
        img = self.screenShot()
        if self.model == 'low':
            maps = img[100:244,15:159]
        elif self.model == 'normal':
            maps = img[100:356,15:271]
        elif self.model == 'hight':
            maps = img[100:356, 15:495]
        elif self.model == 'hight1':
            maps = img[101:487, 15:495]
        self.unknow_count = 0
        self.m_count = 0
        for i in range(self.grid_line):
            for j in range(self.grid_column):
                l_s = i * self.pixel_len
                l_e = i * self.pixel_len + self.pixel_len
                c_s = j * self.pixel_len
                c_e = j * self.pixel_len + self.pixel_len
                res = self.train(maps[l_s:l_e, c_s:c_e])
                self.maps[i][j] = res
                if res == 'unknow':
                    self.unknow_count += 1
                if res == 'm':
                    self.m_count += 1

    def learn(self):
        root_dir='res/'
        lists=os.listdir(root_dir)
        learn_data=[]
        res_data=[]
        for name in lists:
            for file in os.listdir(root_dir + name):
                img_path = root_dir + name + '/' + file
                img = cv2.imread(img_path,0)
                _, img_th = cv2.threshold(img, 170, 255, cv2.THRESH_BINARY)
                line,column=img_th.shape
                tmp_data=[]
                pix_count=0
                for i in range(line):
                    pix_line_count=0
                    for pix in img_th[i]:
                        if pix == 0:
                            pix_count+=1
                            pix_line_count+=1
                        tmp_data.append(pix_line_count)
                img1=img_th.T
                for i in range(column):
                    pix_column_count=0
                    for pix in img1[i]:
                        if pix == 0:
                            pix_column_count+=1
                        tmp_data.append(pix_column_count)
                tmp_data.append(pix_count)
                learn_data.append(tmp_data)

                res_data.append(name)
        print('start train')
        print(res_data)
        self.knn = KNeighborsClassifier()  #引入训练方法 
        self.knn.fit(learn_data,res_data)
        print('finished')
        
    def get_feature(self,srcImg):
        line, column = srcImg.shape
        tmp_data=[]
        pix_count = 0
        for i in range(line):
            pix_line_count=0
            for pix in srcImg[i]:
                if pix == 0:
                    pix_line_count+=1
                tmp_data.append(pix_line_count)
            pix_count+=pix_line_count
        img1=srcImg.T
        for i in range(column):
            pix_column_count=0
            for pix in img1[i]:
                if pix == 0:
                    pix_column_count+=1
                tmp_data.append(pix_column_count)
        tmp_data.append(pix_count)
        return tmp_data
    

    def train_ml(self, srcImg):
        x_test = []
        fea = self.get_feature(srcImg)
        x_test.append(fea)
        res_test = self.knn.predict(x_test) # 获得结果集
        return res_test[0]
        # print(res_test)
    def train(self, srcImg):
        l,c,_ = srcImg.shape
        #print(l,c)
        index_1 = (l + (l&1)) >> 1 
        index_c = (c + (c&1)) >> 1 
        val = list(srcImg[index_1][index_c])

        if val == [255, 0, 0]:
            return '1'
        if val == [0, 128, 0]:
            return '2'
        if val == [0, 0,255]:
            return '3'
        if val == [128,0, 0]:
            return '4'
        if val == [0, 0, 128]:
            return '5'
        if val == [128, 128, 0]:
            return '6'
        '''   
        if srcImg[index_1][index_c] == [0, 128, 0]:
            return '7'
        if srcImg[index_1][index_c] == [0, 128, 0]:
            return '8'
        '''
        if val == [0, 0, 0]:
            if list(srcImg[index_1-3][index_c]) == [0, 0, 255]:
                return 'm'
            else:
                print(val, 'val')
                #print(list(srcImg[index_1-3][index_c]),'l-3,c')
                # cv2.imshow('',srcImg)
                # cv2.waitKey(0)
                # cv2.imwrite('test.png',srcImg)
                raise Exception('err')
            return 'err'
        if val == [192, 192, 192]:
            if list(srcImg[7][1]) == [255, 255, 255]:
                return 'unknow'
            return 'normal'



    def restart_game(self):
        if self.model == 'low':
            self.move_to_window_coordinate(90, 78)
        if self.model == 'normal':
            self.move_to_window_coordinate(145, 78)
        if self.model == 'hight':
            self.move_to_window_coordinate(259, 74)
        self.faker_click()
        shot_img = self.screenShot()
        
        
        # maps = shot_img[101:245,15:159]
        # cv2.imwrite('map_low.png',maps)
        
        self.init_game_mode(shot_img) # 初始化游戏模式
        # self.learn()
        # self.pixel_len = 16
        self.m_count = 0
    
def get_neighbour(l, c):
    line = a.grid_line
    column = a.grid_column
    ls = [l-1, l, l+1]
    cs = [c-1, c, c+1]
    neighbours = []
    data={
        'mine_count':0,
        'unknow_count':0,
        'normal_count':0
    }
    for i in ls:
        for j in cs:
            if [i,j] == [l,c]:
                continue
            if i>=0 and i < line:
                if j >=0 and j < column:
                    neighbours.append([i, j])
                    # print(a.maps[i][j])
                    if a.maps[i][j] == 'm':
                        data['mine_count'] += 1
                    if a.maps[i][j] == 'unknow':
                        data['unknow_count'] += 1
                    if a.maps[i][j] == 'normal' or type(exchange[a.maps[i][j]]) == int:
                        data['normal_count'] += 1
    return neighbours, data

def get_unknow_count(x, y):
    neighbours, _ = get_neighbour(x, y)
    count = 0
    unknow_rect = []
    for x1, y1 in neighbours:
        if a.maps[x1][y1] == 'unknow':
            count += 1
            unknow_rect.append([x1, y1])
    return count, sorted(unknow_rect)

def get_public_unknow_rect(x1,y1,x2,y2):
    _, n1 = get_unknow_count(x1, y1)
    _, n2 = get_unknow_count(x2, y2)
    r = []
    for l in n1:
        if l in n2:
            r.append(l)
    return sorted(r)
    

def get_private_unknow_rect(neighbour, public_unknow_rect):
    count = 0
    r = []
    for l in neighbour:
        if l not in public_unknow_rect and a.maps[l[0]][l[1]] == 'unknow':
            count += 1
            r.append(l)
    return r, count

def clear():
    a.analysis_chessboard()
    line = len(a.maps)
    column = len(a.maps[0])
    for l in range(line):
        for c in range(column):
            if a.maps[l][c] == 'unknow':
                a.move_to_window_grid(l, c)
                a.faker_click()
                        
            
def start_game():
    global isend
    event = 0
    a.analysis_chessboard()
    line = len(a.maps)
    column = len(a.maps[0])
    for l in range(line):
        for c in range(column):
            val = exchange[a.maps[l][c]]
            neighbour, data_info = get_neighbour(l, c)
            if val == 'normal': # 说明四周全是安全区域
                now_event = 0
                for x,y in neighbour:
                    if a.maps[x][y] == 'unknow':
                        a.move_to_window_grid(x, y)
                        # sleep(0.05)
                        a.faker_click()
                        event += 1
                        now_event += 1
                if now_event > 0:
                    a.analysis_chessboard()
                    
            elif type(val) == int:
                
                if val == data_info['mine_count'] + data_info['unknow_count']: # 如果数字等于周围已存在的雷数与未知区域之和，说明未知区域全是雷
                    now_event = 0
                    for x,y in neighbour:
                        if a.maps[x][y] == 'unknow':
                            a.move_to_window_grid(x, y)
                            # sleep(0.05)
                            a.faker_click_right()
                            a.m_count += 1
                            now_event += 1
                            # print(a.m_count,'m_count')
                            event += 1
                    if now_event > 0:
                        a.analysis_chessboard()
                
                elif val == data_info['mine_count']: # 如果数字等于周围已存在的雷数之和，说明未知区域全是安全的
                    now_event = 0
                    for x,y in neighbour:
                        if a.maps[x][y] == 'unknow':
                            a.move_to_window_grid(x, y)
                            # sleep(0.05)
                            a.faker_click()
                            event += 1
                            now_event += 1
                            # a.analysis_chessboard()
                    if now_event > 0:
                        a.analysis_chessboard()
                else: 
 
                    for x, y in neighbour:
                        if type(exchange[a.maps[x][y]]) == int:

                            unknow_count, unknow_rect = get_unknow_count(x, y)
                            public_unknow_rect = get_public_unknow_rect(l, c, x, y)

                            if unknow_rect == public_unknow_rect:
                                neighbour1, data_info1 = get_neighbour(x, y)
                                public_unknow_rect_mine_count = exchange[a.maps[x][y]] - data_info1['mine_count']

                                private_unknow_rect, private_unknow_rect_count = get_private_unknow_rect(neighbour, public_unknow_rect)
 
                                if (val - data_info['mine_count']) == public_unknow_rect_mine_count:
                                    now_event = 0
                                    for x,y in private_unknow_rect:
                                        a.move_to_window_grid(x, y)
                                        a.faker_click()
                                        event += 1
                                        now_event += 1
                                        print('高级策略点击1',x,y)
                                    if now_event > 0:
                                        a.analysis_chessboard()

    if event == 0 and a.m_count < a.all_mine_count:
        if a.unknow_count == 0:
            return
            
        '''高级策略2'''
        now_event = 0
        for l in range(line):
            for c in range(column):
                val = exchange[a.maps[l][c]]
                neighbour, data_info = get_neighbour(l, c)    
                if type(val) == int:
                    for x, y in neighbour:
                        if type(exchange[a.maps[x][y]]) == int:
                            unknow_count, unknow_rect = get_unknow_count(x, y)
                            public_unknow_rect = get_public_unknow_rect(l, c, x, y)
                            if unknow_rect == public_unknow_rect:
                                neighbour1, data_info1 = get_neighbour(x, y)
                                public_unknow_rect_mine_count = exchange[a.maps[x][y]] - data_info1['mine_count']
                                private_unknow_rect, private_unknow_rect_count = get_private_unknow_rect(neighbour, public_unknow_rect)
                                if val - data_info['mine_count'] ==  public_unknow_rect_mine_count + private_unknow_rect_count:
                                    for x,y in private_unknow_rect:
                                        a.move_to_window_grid(x, y)
                                        a.faker_click_right()
                                        now_event += 1
                                        a.m_count += 1
                                        print('高级策略点击222222222222222222222222222222222222222222222',x,y)

        if now_event > 0:
            a.analysis_chessboard()
        if now_event == 0:
            random_click()
    
def random_click():
    a.analysis_chessboard()
    if a.m_count == a.all_mine_count:
        return
    line = len(a.maps)
    column = len(a.maps[0])
    p_map = [ [None  for i in range(a.grid_column)] for j in range(a.grid_line)]
    if a.unknow_count == 0:
        return 
    gobal_p = (a.all_mine_count - a.m_count)/a.unknow_count
    for l in range(line):
        for c in range(column):
            val = exchange[a.maps[l][c]]
            if val == 'unknow':
                neighbour, data_info = get_neighbour(l, c)
                if data_info['unknow_count'] == len(neighbour):
                    p_map[l][c] = gobal_p
                else:    
                    ps = []
                    for x,y in neighbour:
                        val1 = exchange[a.maps[x][y]]
                        if type(val1) == int:
                            neighbour1, data_info1 = get_neighbour(x, y)
                            if data_info1['unknow_count'] != 0 and data_info1['mine_count'] < val1:
                                p = (val1 - data_info1['mine_count'])/data_info1['unknow_count']
                                ps.append(p)
                    if len(ps) > 0:
                        p_map[l][c] = max(ps)
                    else:
                        p_map[l][c] = gobal_p

    min = gobal_p
    min_index = []
    
    for l in range(line):
        for c in range(column):
            if type(p_map[l][c]) == float or type(p_map[l][c]) == int:
                if p_map[l][c] < min:
                    min = p_map[l][c]
                    min_index = []
                    min_index.append([l, c])
                elif p_map[l][c] == min:
                    min_index.append([l, c])

    if len(min_index) == 1:
        x1 = min_index[0][0]
        y1 = min_index[0][1]
    elif len(min_index) == 0:
        print('len 0')
        print(min_index, 'min_index')
        
    else:
        index = randint(0,len(min_index)-1)
        x1 = min_index[index][0]
        y1 = min_index[index][1]
    a.move_to_window_grid(x1, y1)
    a.faker_click()
    print('random', min, gobal_p, x1,y1)
    a.analysis_chessboard()


def test1():
    pixel_len = 16
    index = 1
    img = a.screenShot() #_th()
    # print(img)

    maps = img[101:245,15:159] # 1
    cv2.imshow('',maps)
    cv2.waitKey(0)
    # maps = img[101:357,15:271] # 2

    # maps = img[101:357, 15:495] # 3
    print(maps.shape)
    for i in range(9):
        for j in range(9):
            l_s = i * pixel_len
            l_e = i * pixel_len + pixel_len
            c_s = j * pixel_len
            c_e = j * pixel_len + pixel_len
            cv2.imwrite('{}.png'.format(index),maps[l_s:l_e, c_s:c_e])
            index += 1
    exit()          
    
if __name__ == '__main__':
    exchange = {
        '1': 1,
        '2': 2,
        '3': 3,
        '4': 4,
        '5': 5, 
        '6': 6,
        '7': 7,
        '8': 8,
        'unknow': 'unknow',
        'normal':'normal',
        'm':'m',
        'err':'err',
        None:None
    }
    a = SL()
    #test1()
    isend = False
    a.move_to_window_grid(randint(0,a.grid_line),randint(0,a.grid_column))

    a.faker_click()
    a.analysis_chessboard()

    while a.m_count < a.all_mine_count :#and not isend:
        start_game()

    clear()
