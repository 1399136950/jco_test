#!/d/python-37-32/python
from tkinter import *
import os
import re

class MainWindow:
    def __init__(self):
        self.frame = Tk()
        self.label_net = Label(self.frame,text = "IP:")
        self.text_net = Entry(self.frame, width="50")
        self.label_net.grid(column=0,row=0)
        self.text_net.grid(column=1,row=0)
        self.button_ok = Button(self.frame,text = "添加",width = 10)
        self.button_ok.bind("<ButtonPress>",self.buttonclick)
        self.button_ok.grid(column=0,columnspan=2,row=1)
        self.text_info=Text(self.frame,width=50,height=10)
        self.text_info.grid(column=0,columnspan=2,row=2)
        self.frame.mainloop()
	
    def buttonclick(self,event):
        net_ip=self.text_net.get()
        cmd="netsh int ip add address 本地连接 {} 255.255.255.0".format(net_ip)
        res=os.popen(cmd)
        info=res.read()
        if len(info)==1:
            self.text_info.insert(END,"success\n")
        else:
            #self.text_info.insert(END,info)
            self.text_info.insert(END,info)
            #print(info.encode('gbk').decode('gbk'))
frame = MainWindow()
