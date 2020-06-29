from BST import BST,Element
from random import randint

RED = 'red'
BLACK = 'black'


class RBElement():

    def __init__(self, val=None, parent=None, left=None, right=None, color=RED):
        self._val = val
        self._parent = parent
        self._left = left
        self._right = right
        self._color = color

    def __repr__(self):
        return '<RBElement object> <_val>:{} <_color>:{}'.format(self._val,self._color)

class RBT(BST):

    def __init__(self, element):
        super().__init__(element)
        
    def add(self, val):
        x = self._root
        if x == None:
            self._root = RBElement(val, color=BLACK)
        else:
            while x != None:
                y = x
                if val > x._val:
                    x = x._right
                else:
                    x = x._left
            e = RBElement(val, parent=y, color=RED)
            if val > y._val:
                y._right = e
            else:
                y._left = e
            self.recolor(e)
            
    def recolor(self, e):
        p = e._parent
        if p == None:
            pass
        elif p._color == RED:
            if p._parent == None:
                p._color = BLACK
            else:
                u = None
                if p._parent._left == p:
                    u = p._parent._right    # 当前节点的叔叔节点
                elif p._parent._right == p:
                    u = p._parent._left
                if u == None:
                    u = RBElement(color=BLACK)
                if u._color == RED:
                    p._color = BLACK
                    u._color = BLACK
                    p._parent._color = RED
                    self.recolor(p._parent)
                elif u._color == BLACK:
                    if p._parent._left == p:
                        self.right_rolate(p._parent)
                    else:
                        self.left_rolate(p._parent)
                    p._color = BLACK
                    if p._parent != None:
                        p._parent._color = RED
                self._root._color = BLACK
    
            

if __name__ == '__main__':
    rbt = RBT(RBElement(98, color=BLACK))
    for i in range(20):
        rbt.add(randint(0,1000))
    
