from download import Download
import tkinter as tk
from tkinter import ttk

class Gui:
    def __init__(self):
        self.init_tk()

    def init_tk(self):
        self.root=tk.Tk()

        self.download_frame=tk.Frame(self.root)
        self.download_frame_up=tk.Frame(self.download_frame)

        self.entry_url=tk.Entry(self.download_frame_up)
        self.entry_name=tk.Entry(self.download_frame_up)
        self.button=tk.Button(self.download_frame_up,text='下载')
        self.entry_url.grid()
        self.entry_name.grid()
        self.button.grid()

        
        self.download_frame_down=tk.Frame(self.download_frame)
        self.text=tk.Text(self.download_frame_down)
        self.text.grid()


        self.download_frame_up.grid()
        self.download_frame_down.grid()


        self.info_frame=tk.Frame(self.root)
        col = ['1','2','3','4']
        self.tree=ttk.Treeview(self.info_frame,columns = col, height = 10, show = "headings")
        self.tree.heading("1", text="coulmn 1")#设置表头
        self.tree.heading("2", text="column 2")
        self.tree.heading("3", text="coulmn 3")
        self.tree.heading("4", text="column 4")
        self.tree.grid()
        self.download_frame.grid()

        self.menubar=tk.Menu()
        self.menubar.add_command(label='下载')
        self.menubar.add_command(label='详情',command=self.show_info)
        self.root['menu']=self.menubar
    
    def show_info(self):
        
        self.download_frame.forget_grid()
        self.download_info.grid()
        
    def main(self):
        self.root.mainloop()


a=Gui()
a.main()
