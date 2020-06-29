import re
import time
import struct

l=[str(i) for i in range(1000000)]


s=time.time()
''.join(l)
e=time.time()
print(e-s)

s=time.time()
r=''
for i in l:
    r+=i    

e=time.time()
print(e-s)
