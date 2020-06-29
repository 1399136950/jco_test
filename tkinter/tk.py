import tkinter
 
#主窗口：
 
window= tkinter.Tk()
 
window.title("简易版微信小程序")
 
window.resizable(width=False, height=False)# 窗口大小不可改变
 
window.geometry("1000x800+650+100")
 
#顶级菜单，显示在窗口最上方
 
menubar= tkinter.Menu(window)
 
#fmenu可理解为菜单容器，用于add菜单项
 

 
fmenu4=tkinter.Menu(window)#创建了第四个菜单容器，add四个菜单容器，实现多级子菜单
 
fmenu4_1=tkinter.Menu(window)
 
fmenu4_1.add_command(label='菜单4-子菜单1-1')
 
fmenu4_1.add_command(label='菜单4-子菜单1-2')
 
fmenu4_2=tkinter.Menu(window)
 
fmenu4_2.add_command(label='菜单4-子菜单2-1')
 
fmenu4_2.add_command(label='菜单4-子菜单2-2')
 
fmenu4_3=tkinter.Menu(window)
 
fmenu4_3.add_command(label='菜单4-子菜单3-1')
 
fmenu4_3.add_command(label='菜单4-子菜单3-2')
 
fmenu4_4=tkinter.Menu(window)
 
fmenu4_4.add_command(label='菜单4-子菜单4-1')
 
fmenu4_4.add_command(label='菜单4-子菜单4-2')
 
#将fmenu4_1,fmenu4_2,fmenu4_3,fmenu4_4四个菜单容器加入fmenu4菜单容器中
 
fmenu4.add_cascade(label='菜单4-子菜单1', menu=fmenu4_1)
 
fmenu4.add_cascade(label='菜单4-子菜单2', menu=fmenu4_2)
 
fmenu4.add_cascade(label='菜单4-子菜单3', menu=fmenu4_3)
 
fmenu4.add_cascade(label='菜单4-子菜单4', menu=fmenu4_4)
 
#将“fmenu1、fmenu2、fmenu3、fmenu4”四个菜单容器加入顶级菜单中，并设置该菜单容器的label
 

 
menubar.add_cascade(label='菜单4',menu=fmenu4)
 
window['menu']= menubar#设置窗口的菜单为menubar
 
window.mainloop()
