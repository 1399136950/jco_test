from matplotlib import pyplot as plt
import numpy as np

def y_fun(num):
    return num**3+2*num

def y_d_fun(num):
    return 2*num**2+2

def y_q_fun(k,x0,y0,x):
    return k*(x-x0)+y0

x = np.linspace(-12, 10, 300)
y=[y_fun(n) for n in x]
plt.plot(x,y)
for i in [1,5,9]:
    x0=i
    k=y_d_fun(x0)
    y0=y_fun(x0)
    plt.scatter(x0,y0)
    xx = np.linspace(-10, 10, 300)
    yy=[y_q_fun(k,x0,y0,n) for n in xx]

    plt.plot(xx,yy)
plt.show()

