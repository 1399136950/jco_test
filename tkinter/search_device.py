import socket
import threading
from time import sleep
from collections import defaultdict
import tkinter as tk
from tkinter import ttk
class Search():
    
    def __init__(self):
        self.con=True
        self.broadcastPort=8002
        self.listenPort=33010
        self.mac='50-E5-49-C9-93-03'
        self.hostIp='192.168.0.101'
        self.search_time=4
    
    def sendUdpMsg(self):#{//发送UDP消息
        msg="SEARCH * HDS/1.0 nLOCALIP={}#LOCALPORT={}#LOCALMAC=#{}".format(self.hostIp,self.listenPort,self.mac)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.SOL_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        for i in range(20):
            sock.sendto(msg.encode(),('255.255.255.255', self.broadcastPort))
            sleep(0.2)
        sock.close()

    def getUdpMsg(self):
        s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.SOL_UDP)
        s.setblocking(False)
        s.bind(('0.0.0.0',self.listenPort))
        address_hash_map=defaultdict(bool)
        self.info=defaultdict(str)
        while self.con:
            try:
                data,address = s.recvfrom(65535)
            except:
                pass
            else:
                if address_hash_map[address[0]]==False:
                    address_hash_map[address[0]]=True
                    res={}
                    data=data.decode().split('\r\n')
                    for t in data:
                        tmp=t.split(':')
                        if len(tmp)>=2:
                            key=tmp[0]
                            info=t.split(key+':')[1]
                            res[key]=info
                    self.info[address[0]]=res
        s.close()
        self.con=True

        for key in address_hash_map:
            print(self.info[key])
            # pass
        print(len(self.info))
        print(len(address_hash_map))
        

    def search(self):
        send_thread=threading.Thread(target=self.sendUdpMsg)
        send_thread.start()
        get_thread=threading.Thread(target=self.getUdpMsg)
        get_thread.start()
        sleep(self.search_time)
        self.con=False
        send_thread.join()
        get_thread.join()
        print('ok')

class SearchTool():
    
    def __init__(self):
        self.exit_flag=False
        self.search_thread_is_exit=False
        self.con=threading.Condition()
        self.search_server=Search()
        self.init_tk()
        search_service=threading.Thread(target=self.search_thread)
        search_service.daemon=True
        search_service.start()
        self.root.mainloop()
    
    def init_tk(self):
        self.root=tk.Tk()
        self.menubar = tk.Menu(self.root)
        self.menubar.add_command(label = "search", command = self.start_search)
        self.root.config(menu = self.menubar)
        self.tree=ttk.Treeview(self.root,columns = ['ip','ID','MAC','Platform'],show="headings")
        self.tree.column("Platform",width=400)
        self.tree.heading("ip", text="ip",)
        self.tree.heading("ID", text="ID")
        self.tree.heading("MAC", text="MAC")
        self.tree.heading("Platform", text="Platform")
        self.tree.grid(row=0,column=0)
        self.scrollbar =tk.Scrollbar(self.root)

        self.scrollbar.grid(row=0,column=0,sticky=tk.E+tk.N+tk.S)
        self.scrollbar.config(command=self.tree.yview)#绑定拖动
        self.tree.config(yscrollcommand=self.scrollbar.set)#绑定设置滚动条
        self.root.protocol("WM_DELETE_WINDOW",self.on_closing)
        
    def search_thread(self):
        while True:
            with self.con:
                print('wait')
                self.con.wait()
            if self.exit_flag:
                print('search_thread exit')
                break
            else:
                print('search now')
                self.search_server.search()
                if not self.exit_flag:
                    for ip in self.search_server.info:
                        #self.text.insert('end','{}\n'.format(self.search_server.info[key]))
                        self.tree.insert('','end',values=('{}'.format(self.search_server.info[ip]['Device-IP']),self.search_server.info[ip]['Device-ID'],self.search_server.info[ip]['Device-Mac'],self.search_server.info[ip]['Device-VerServer']))
                        #self.text.insert('end','{}\n'.format(self.search_server.info[key]))
                        #print(self.search_server.info[ip])
        self.search_thread_is_exit=True
            
            
    def on_closing(self):
        self.exit_flag=True
        self.root.destroy()
        while not self.search_thread_is_exit:
            with self.con:
                self.con.notify()
            sleep(0.1)
        self.root.quit()
    
    def start_search(self):
        print('wakeup search_thread')
        with self.con:
            self.con.notify()
            
    
# a=SearchTool()
