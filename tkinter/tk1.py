import tkinter as tk

root=tk.Tk()

menubar= tk.Menu(root,tearoff=0)

menu=tk.Menu(root,tearoff=0)

menu1=tk.Menu(root,tearoff=0)
menu1.add_command(label='删除日志',command=lambda:3)
menu1.add_command(label='删除视频',command=lambda:3)
menu1.add_command(label='删除日志和视频',command=lambda:3)

menu2=tk.Menu(root,tearoff=0)
menu2.add_command(label='添加日志',command=lambda:3)
menu2.add_command(label='添加视频',command=lambda:3)
menu2.add_command(label='添加日志和视频',command=lambda:3)

menu.add_cascade(label='删除',menu=menu1)
menu.add_cascade(label='添加',menu=menu2)

menubar.add_cascade(label='选项',menu=menu)

root['menu']=menubar

root.mainloop()
