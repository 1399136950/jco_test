import tkinter as tk
from tkinter import ttk
from time import sleep
def handler(event):
    print('click two')
    text=tk.Text(width=10,height=1)
    text.grid(row=0,column=0)

root=tk.Tk()
col = ['1','2','3','4']
tree=ttk.Treeview(root,columns = col, height = 10, show = "headings")
tree.heading("1", text="coulmn 1")
tree.heading("2", text="column 2")
tree.heading("3", text="coulmn 3")
tree.heading("4", text="column 4")
tree.grid()

tree.insert('',0,values=('a','b','c','v'))
tree.insert('',1,values=('a','b','d','v'))

x=tree.get_children()
for item in x:
    item_text = tree.item(item, "values")#
    print(item_text)
    #tree.set(item, column='2', value='test')
#print(x)
root.mainloop()
