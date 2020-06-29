from time import time
fd=open('1.jpg','rb')
fd1=open('1.txt','ab')
s=time()
content=fd.read()
s=time()
for i in range(50):
    fd1.write(content)


e=time()
print(e-s)
