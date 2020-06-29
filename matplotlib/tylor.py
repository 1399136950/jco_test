import numpy as np
from matplotlib import pyplot as plt

def f6(x):
    return 1+x+x**2/2+x**3/6+x**4/24+x**5/120+x**6/720
def f5(x):
    return 1+x+x**2/2+x**3/6+x**4/24
def f4(x):
    return 1+x+x**2/2+x**3/6
x=np.linspace(-2,4,500)
ex=[np.e**i for i in x]
ex6=[f6(i) for i in x]
ex5=[f5(i) for i in x]
ex4=[f4(i) for i in x]
plt.plot(x,ex,c='y')
plt.plot(x,ex4,c='g')
plt.plot(x,ex5,c='r')
plt.plot(x,ex6,c='b')
plt.show()
