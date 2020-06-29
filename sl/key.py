import win32con
import win32api
import time


class Key:
    
    key_map = {
        "0": 49,
        "1": 50,
        "2": 51,
        "3": 52,
        "4": 53,
        "5": 54,
        "6": 55,
        "7": 56,
        "8": 57,
        "9": 58,
        "A": 65,
        "B": 66,
        "C": 67,
        "D": 68,
        "E": 69,
        "F": 70,
        "G": 71,
        "H": 72,
        "I": 73,
        "J": 74,
        "K": 75,
        "L": 76,
        "M": 77,
        "N": 78,
        "O": 79,
        "P": 80,
        "Q": 81,
        "R": 82,
        "S": 83,
        "T": 84,
        "U": 85,
        "V": 86,
        "W": 87,
        "X": 88,
        "Y": 89,
        "Z": 90,
        "BACKSPACE": 8,
        "TAB": 9,
        "ENTER": 13,
        "SHIFT": 16,
        "CTRL": 17,
        "ALT": 18,
        "ESC": 27,
        "F1": 0x70,
        "F2": 0x71,
        "F3": 0x72,
        "F4": 0x73,
        "F5": 0x74,
        "F6": 0x75,
        "F7": 0x76,
        "F8": 0x77,
        "F9": 0x78,
        "F10": 0x79,
        "F11": 0x7A,
        "F12": 0x7B
    }
     
    def _key_down(self, key):
        """
        函数功能：按下按键
        参    数：key:按键值
        """
        key = key.upper()
        vk_code = self.key_map[key]
        win32api.keybd_event(vk_code, win32api.MapVirtualKey(vk_code,0), 0, 0)
     
     
    def _key_up(self, key):
        """
        函数功能：抬起按键
        参    数：key:按键值
        """
        key = key.upper()
        vk_code = self.key_map[key]
        win32api.keybd_event(vk_code, win32api.MapVirtualKey(vk_code, 0), win32con.KEYEVENTF_KEYUP, 0)
     
     
    def key_press(self, key_name):
        """
        函数功能：点击按键（按下并抬起）
        参    数：key:按键值
        """
        self._key_down(key_name)
        time.sleep(0.02)
        self._key_up(key_name)       
        
    def compose_key_press(self, *args):
        """
        函数功能：组合按键
        """
        l = list(args)
        for i in range(len(l)):
            self._key_down(l[i])
            time.sleep(0.02)
        while len(l)>0:
            self._key_up(l.pop())
            time.sleep(0.02)
            



if __name__ == '__main__':
    k = Key()
    time.sleep(1)
    k.compose_key_press('Ctrl','c')
