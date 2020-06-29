import tkinter as tk
import cv2
from PIL import Image, ImageTk
from threading import Thread

def open_stream(can,root,ip):
    cap = cv2.VideoCapture("rtsp://"+ip+"/stream2")
    
    w=cap.get(3)
    h=cap.get(4)
    frame_rate=cap.get(5)
    fourcc = cv2.VideoWriter_fourcc('D','I','V','X')
    videoWriter = cv2.VideoWriter('oto_other.avi',fourcc , frame_rate, (int(w),int(h)),True)  
    global play_status,tkImage
    while play_status:
        
        ret,frame=cap.read()
        videoWriter.write(frame)
        #cvimage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        #pilImage=Image.fromarray(cvimage)
        #tkImage = ImageTk.PhotoImage(image=pilImage)
        #can.create_image(0,0,anchor='nw',image=tkImage)
        #can.image=tkImage
    cap.release()
    videoWriter.release()
    print('exit')

def main():
    global play_status
    if play_status:
        print('already playing')
        play_status=False
        button.config(text='开始')
    else:
        play_status=True
        button.config(text='停止')
        ip=entry.get()
        thread=Thread(target=open_stream,args=(can,root,ip))
        thread.daemon=True
        thread.start()
        print('playing now')

play_status=False
tkImage=None
root=tk.Tk()
can=tk.Canvas()
can.config(width=800)
can.config(height=600)
entry=tk.Entry()
button=tk.Button(text='开始',command=main)
can.grid(row=0,column=0)
entry.grid(row=1,column=0)
button.grid(row=2,column=0)
menu=tk.Menu(root)
menu.add_command(label = "Quit",command=quit)
root.config(menu=menu)
root.mainloop()

