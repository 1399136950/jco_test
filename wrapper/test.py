from functools import wraps
from time import time,sleep

def warp(func):
    a = 1
    def test_func(*args, **kwds):

        #nonlocal a

        a+=3
        func(*args, **kwds)
        print(a)

    return test_func



@warp
def test():
    pass



if __name__ == '__main__':
    pass
