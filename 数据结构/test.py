from ring_queue import RingQueue

length = 100
r = RingQueue(length)

[r.put(i) for i in range(length)]
'''
for i in range(length):
    res = r.get()
    if res == length - i - 1:
        pass
    else:
        print('err')
'''
