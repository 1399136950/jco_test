import tkinter as tk
def a():
    print('a')
def b():
    print('b')
def c():
    print('c')
root=tk.Tk()
menu = tk.Menu(root, tearoff=0)
menu.add_command(label="复制", command=a)
menu.add_separator()#画分割线
menu.add_command(label="粘贴", command=b)
menu.add_separator()
menu.add_command(label="剪切", command=c)
def popupmenu(event):
    menu.post(event.x_root, event.y_root)
root.bind("<Button-3>", popupmenu)
root.mainloop()
