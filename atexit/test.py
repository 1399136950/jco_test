import atexit
from time import sleep

@atexit.register
def test():
    print('exit')


