from time import sleep
import sys
str1='*'

for i in range(101):
    sys.stdout.write('\r'+str1*i+(100-i)*' '+'|{}%'.format(i))
    sleep(1)
    # sys.stdout.flush()
