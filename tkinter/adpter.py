import tkinter as tk
import threading
from time import sleep
def handle_adapter(func,**args):
    return lambda event,func=func,args=args:func(event,**args)

def handle(event,**args):
    def test():
        str1='>'
        for i in range(101):
            #sys.stdout.write('\r'+str1*i+(100-i)*'  '+'|{}%'.format(i))

            text.delete(0.0, tk.END)
            text.insert(tk.INSERT,str1*i+(100-i)*' '+'|{}%'.format(i))
            sleep(0.1)
        #args['lb']['text']='you are in this'
        print(event)
    th=threading.Thread(target=test).start()

def leave(event,**args):
    args['lb']['text']=args['val']
    print(event)
root=tk.Tk()
frame=tk.Frame(root)
for i in range(10):
    str1='hello world '+str(i)
    label=tk.Label(frame,text=str1)
    label.grid(column=0,row=i)

    label.bind('<Button-1>',handle_adapter(func=handle,lb=label))
    #label.bind('<Leave>',handle_adapter(func=leave,lb=label,val=str1))
frame.grid(column=0,row=0)

text_frame=tk.Frame(root)
text=tk.Text(text_frame,width=150)
text.grid(column=0,row=0)
text_frame.grid(column=1,row=0)
root.mainloop()
