import tkinter as tk
import cv2
from PIL import Image, ImageTk
from threading import Thread
IP='192.168.201.145'
cap = cv2.VideoCapture("rtsp://"+IP+":80/stream2")
def open_stream():
    ret,frame=cap.read()
    cvimage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    pilImage=Image.fromarray(cvimage)
    tkImage = ImageTk.PhotoImage(image=pilImage)
    return  tkImage 



def main():
    global play_status
    if play_status:
        print('already playing')
        play_status=False
        button.config(text='开始')
    else:
        play_status=True
        button.config(text='停止')
        #thread=Thread(target=open_stream,args=(can,root))
        #thread.start()
        print('playing now')

play_status=False
tkImage=None
root=tk.Tk()
can=tk.Canvas()
button=tk.Button(text='开始',command=main)
can.grid(row=0,column=0)
button.grid(row=1,column=0)
menu=tk.Menu(root)
menu.add_command(label = "Quit")
root.config(menu=menu)
#root.mainloop()

while True:
    tkImage=open_stream()
    can.create_image(0,0,anchor='nw',image=tkImage)
    root.update()



