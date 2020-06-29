from threading import Lock,Condition


class RingQueue():

    def __init__(self, length):
        self.length = length
        self._data = [None] * length
        self.start = 0
        self.now_len = 0
        self.lock = Lock()
        self.con = Condition()

    def __repr__(self):
        return '<length>: [{}], <start>: [{}], <now_len>: [{}], <data>: [{}]'.format(self.length, self.start, self.now_len, self._data)

    def put(self, ele):
        with self.lock:
            if self.now_len == self.length: # 队列满了
                self._data[self.start] = ele    #  
                self.start = (self.start + 1) % self.length
                with self.con:
                    self.con.notify()
            else:
                index = (self.start + self.now_len) % self.length
                self._data[index] = ele
                self.now_len += 1
                with self.con:
                    self.con.notify()

    def get(self):
        if self.now_len == 0:
            with self.con:
                self.con.wait()
        with self.lock:
            index = (self.start + self.now_len) % self.length - 1 # 返回尾部元素
            # index = self.start  # 返回首部元素
            # self.start = (self.start + 1) % self.length # 返回首部元素添加的操作
            
            '''其他都是一样的'''
            self.now_len -= 1
            ele = self._data[index]
            self._data[index] = None
            return ele

    def clear(self):
        with self.lock:
             self._data = [None] * self.length
             self.start = 0
             self.now_len = 0
