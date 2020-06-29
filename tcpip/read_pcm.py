import struct
from matplotlib import pyplot as plt

fd = open('192.168.201.19.pcm','rb')
y = []
f=struct.Struct('<h')
while True:
    audio_sample = fd.read(2)
    if audio_sample == b'':
        break
    y.append(f.unpack(audio_sample)[0])
fd.close()

x = [i for i in range(len(y))]
xs=[0,0]
ys=[1,1]
i=0
setp = 10
while i+setp < len(x):
    
    xs[0] = x[i]
    xs[1] = x[i+setp]
    ys[0] = y[i]
    ys[1] = y[i+setp]
    plt.plot(xs, ys, c='r')
    plt.pause(0.00001)
    i += setp
plt.show()



