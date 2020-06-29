from random import randint
from queue import Queue

class Element():

    def __init__(self, val, parent=None, left=None, right=None):
        self._parent = parent
        self._left = left
        self._right = right
        self._val = val

    def __repr__(self):
        return '<Element object><_val>:{}'.format(self._val)

class BST:

    def __init__(self, element):
        self._root = element

    def add(self, val):
        x = self._root
        y = None
        while x != None:
            y = x
            if val > x._val:
                x = x._right
            else:
                x = x._left
        if y == None:
            self._root = Element(val)
        else:   
            e = Element(val, y)
            if y._val < val:
                y._right = e
            else:
                y._left = e

    def dump(self,element,index,height,l):
        if element != None:
            left = element._left
            right = element._right
            self.dump(left, index+1,height,l)
            l[index].append(element._val)
            # print('{}{}'.format('-'*index, element._val))
            self.dump(right, index+1,height,l)
        else:
            if index < height:
                l[index].append(' ')

    def print_tree(self):
        height = self.get_tree_height()
        l = [[]*i for i in range(4)]
        self.dump(self._root, 0, height,l)
        [print(i) for i in l]
            
    def dump1(self,element=None,index=0):
        if element != None:
            left = element._left
            right = element._right
            self.dump1(left, index+1)
            print('{}{}'.format('-'*index, element._val))
            self.dump1(right, index+1)
            
    def min(self, element=None):
        x = element
        if x == None:
            return None
        while x._left != None:
            x = x._left
        return x
            
    def max(self, element=None):    # 当前节点往下的最大节点
        x = element
        if x == None:
            return None    
        while x._right != None:
            x = x._right
        return x

    def get_element_deep(self, e):  # 获取元素深度,从上往下
        x = e
        if x == None:
            return 0
        deep = 1
        while x._parent != None:
            x = x._parent
            deep += 1
        return deep
    
    def get_tree_height(self):    # 获取元素高度,从下往上
        e = self._root
        l = e._left
        r = e._right
        return max(self._get_element_height(l),self._get_element_height(r))+1
    
    def tree_height(self):
        q = Queue() # 先进先出队列
        if self._root == None:
            return 0
        q.put(self._root)
        count = 0   # 当前层中已经遍历的节点数  
        next_count = 1  # 还未进行遍历的下一层的节点数
        tree_height = 0 # 树高
        while q.qsize() > 0:
            e = q.get()
            count += 1
            if e._left != None:
                q.put(e._left)
            if e._right != None:
                q.put(e._right)
            if count == next_count:     # 当前遍历的节点数和当前层的节点数相等时,即一层的节点遍历完成
                next_count = q.qsize()  # 此时队列中的元素都是下一层节点
                count = 0   # 置下一层中已经遍历的节点数量为0
                tree_height += 1    # 遍历完一层 树高加1
        return tree_height

    def _get_element_height(self, e):
        if e == None:
            return 0
        else:
            l = e._left
            r = e._right
            l_l = self._get_element_height(l)
            r_l = self._get_element_height(r)
            return max(l_l, r_l)+1

    def find(self, val):    # 查找值
        e = self._root
        if e == None:
            return None
        if e._val == val:
            return e
        while e != None:
            if e._val < val:
                e = e._right
            elif e._val > val:
                e = e._left
            else:
                return e
        return e
    
    def successor(self, element):   # 找到后继节点
        if not isinstance(element, Element):
            raise Exception('element must be Element object')
        if element._right != None:
            return self.min(element._right)
        else:
            x = element
            while x._parent != None and x == x._parent._right:
                x = x._parent
            return x._parent

    def precursor(self, element):   # 前驱节点
        if not isinstance(element, Element):
            raise Exception('element must be Element object')
        if element._left != None:
            return self.max(element._left)
        else:
            x = element
            while x._parent != None and x == x._parent._left:
                x = x._parent
            return x._parent
    
    def replace_element(self, e1, e2):  # 用e2替换e1
        e2._parent = e1._parent
        if e1._parent == None:
            self._root = e2
        else:
            if e1._parent._left == e1:
                e1._parent._left = e2
            else:
                e1._parent._right = e2
        
    def delete(self, element):  # 删除元素
        if element._left == None and element._right == None:
            p = element._parent
            if p == None:
                self._root = None
            elif p._left == element:
                p._left = None
            elif p._right == element:
                p._right = None
        elif element._left != None and element._right != None:   # 两个孩子
            y = self.min(element._right)    # element的后继节点;因为element存在右孩子，所以其后继节点一定是其右子树的最小值,并且这个节点没有左孩子
            if y == element._right:    # 后继节点刚好是element的右孩子
                self.replace_element(element, element._right)   # 用右孩子替代自己
                element._right._left = element._left    # 新节点的左孩子等于之前节点的左孩子
                element._right._left._parent = element._right   # 新节点的左孩子的父亲等于当前新节点
            else:
                if y._right != None:
                    self.replace_element(y, y._right)
                else:
                    if y._parent._left == y:
                        y._parent._left = None
                    else:
                        y._parent._right = None
                self.replace_element(element, y)
                y._left = element._left
                y._right = element._right
                y._left._parent = y
                y._right._parent = y
                
        else:   # 只有一个孩子
            if element._left == None:
                self.replace_element(element, element._right)
            else:
                self.replace_element(element, element._left)

    def left_rolate(self, e):   # 左旋转操作,需要有右孩子
        y = e._right
        if y != None:
            y._parent = e._parent
            e._right = y._left
            if e._parent == None:
                self._root = y
            elif e._parent._left == e:
                e._parent._left = y
            else:
                e._parent._right = y
            y._left = e

    def right_rolate(self, e):  # 右旋转操作，需要有左孩子
        y = e._left
        if y != None:
            e._left = y._right
            y._parent = e._parent
            if e._parent == None:
                self._root = y
            elif e._parent._left == e:
                e._parent._left = y
            elif e._parent._right == e:
                e._parent._right = y
            y._right = e



if __name__ == '__main__':
    bst = BST(Element(45))
    bst.add(96)
    bst.add(64)
    bst.add(107)
    bst.add(105)
    bst.add(112)
    bst.dump1(bst._root)
    for i in range(2000):
        bst.add(randint(0,80000))
