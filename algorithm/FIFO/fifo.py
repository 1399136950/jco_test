class FIFO:
    
    def __init__(self):

        self._size = 0

        self.max_size = 10
        
        self._data = [None]*self.max_size

        self._first = 0
        

    def __len__(self):

        return self._size


    def __repr__(self):

        return str(self._data)
    
    
    def put(self,data):

        if self._size == self.max_size:

            self.resize()
        
        index = (self._first + self._size)%len(self._data)

        self._data[index] = data

        self._size += 1


    def put_left(self,data):

        if self._size == self.max_size:

            self.resize()

        index = (self._first - 1 + self.max_size)%self.max_size

        self._data[index] = data

        self._first = index

        self._size += 1
    

    def pop_left(self):

        if self._size == 0:

            raise Exception('index error')

        tmp = self._data[self._first]

        self._data[self._first] = None
        
        self._first = (self._first+1)%len(self._data)

        self._size -= 1

        return tmp


    def pop(self):

        if self._size == 0:

            raise Exception('index error')

        index = (self._first + self._size) % self.max_size
        
        tmp = self._data[index-1]

        self._data[index-1] = None

        self._size -= 1

        return tmp
 
    
    def resize(self):

        print('new size:', 2*self.max_size)
        
        data = [None] * self.max_size

        for i in range(self._first, self._first+self.max_size):

            if i >= self.max_size:

                index =  i % self.max_size

                data[index], self._data[index] = self._data[index], None

        self._data.extend(data)

        self.max_size = 2 * self.max_size

class FIFO_OLD(FIFO):

    def resize(self):

        print('new size:', 2*self.max_size)
        
        data = [None] * (2*self.max_size)

        for i in range(self._first, self._first+self.max_size):

            data[i-self._first] = self._data[i % self.max_size]

        self._data=data

        self._first = 0

        self.max_size = 2 * self.max_size

if __name__ == '__main__':

    from time import time
    size=190
    a = FIFO()
    s=time()
    for i in range(size):
        a.put(i)
    e=time()
    print(e-s)

