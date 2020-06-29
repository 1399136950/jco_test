from tkinter import *
import os
import re

class MainWindow:
    exitflag=1
    threadnum=6
    def __init__(self):
        self.frame = Tk()
        
        self.label_net = Label(self.frame,text = "网段:")
        self.text_net = Entry(self.frame, width="50")
        self.label_net.grid(column=0,row=0)
        self.text_net.grid(column=1,row=0)
        
        self.button_ok = Button(self.frame,text = "添加",width = 10)
        self.button_ok.bind("<ButtonPress>",self.buttonclick)
        self.button_ok.grid(column=0,columnspan=2,row=1)
        
        self.text_info=Text(self.frame)
        self.text_info.grid(column=0,columnspan=2,row=2)
        
        self.frame.mainloop()
	
    def buttonclick(self,event):
        net=self.text_net.get()
        if re.match('^\d+$',net)==None:
            self.text_info.insert(END,"input err'\r\n")
        else:
            if int(net)>=0 and int(net)<=255:
                cmd="netsh int ip add address 本地连接 192.168.{}.101 255.255.255.0".format(net)
                res=os.system(cmd)
                if res==0:
                    self.text_info.insert(END,"success\r\n")
                else:
                    self.text_info.insert(END,"{}\r\n".format('地址已经存在'))
            else:
                self.text_info.insert(END,"input err\r\n")
               

frame = MainWindow()