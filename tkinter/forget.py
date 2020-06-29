import tkinter as tk
from time import sleep

def show():
    button1.grid_forget()
    button2.grid(column=0,row=0)
    label['text']='hello ASDASD world'
    frame3.grid(column=0,row=1)
def hidden():
    button2.grid_forget()
    button1.grid(column=1,row=0)
    frame3.grid_forget()

root=tk.Tk()

frame_head=tk.Frame(root)
frame_head_left=tk.Frame(frame_head)
frame_head_right=tk.Frame(frame_head)
frame_head.grid(column=0,row=0)
label1=tk.Label(frame_head_left,text='hello')
label2=tk.Label(frame_head_right,text='world')
label1.grid(column=0,row=0)
label2.grid(column=0,row=0)
frame_head_left.grid(column=0,row=0)
frame_head_right.grid(column=1,row=0)
root.mainloop()
