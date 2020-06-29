class Test():
    def __init__(self, name):
        self._name = name
    
    @property
    def name(self):
        print(self._name)
    
    @name.setter
    def name(self, val):
        self._name = val
    
if __name__ == '__main__':
    a=Test('xj')
