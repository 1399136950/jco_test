import numpy as np
from random import randint
import matplotlib.pyplot as plt
y=[]
x=np.linspace(0,10,100,int)
for i in x:
    y.append(i**2+randint(-10,10))
w=[1,1,1]
alapha=0.04#学习率
#y=k*x**2+b*x+c
for i in range(len(x)):
    input=np.mat([x[i]**2,x[i],1]).T
    #print(w*input)
x=[i for i in range(-20,40)]
y=[(i-10)**2 for i in x]
plt.scatter(x,y,marker='.')
plt.show()
