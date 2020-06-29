class Tree():

    class _Node():
        def __init__(self,e,parent=None):
            self._element=e
            self.parent=parent
            self.children=[]

    class Position():
        def __init__(self,container,node):
            self._container=container
            self._node=node

        def element(self):
            return self._node._element

    def _validate(self,p):
        if not isinstance(p,self.Position):
            print('err')
        if p._container is not self:
            print('err')
        if p._node._parent is p._node:
            print('err')
        return p._node

    def _make_position(self,node):
        if node is not None:
            return self.Position(self,node)
        else:
            return None
            
    def __init__(self):
        self.root=None
        self.size=0
    
    def is_root(self,e):
        if e is self.root:
            return True
        else:
            return False
    
    def childrens(self,e):
        return e._node.children
    
    def parent(self,e):
        return e._node.parent

    def brothers(self,e):
        tmp = list(self.childrens(self.parent(e)))
        tmp.remove(e)
        return tmp
    
    def height(self,e):
        pass
    
    def deep(self,e):
        if self.is_root(e):
            return 1
        else:
            return 1+self.deep(self.parent(e))
    
    def add(self,e,parent=None):
        n=self._Node(e,parent)
        tmp=self._make_position(n)
        tmp.parent=parent
        if parent is not None and self.root is not None:
            parent._node.children.append(tmp)
            self.size+=1    
        else:    
            if parent is None and self.root is None:
                self.root=tmp
                self.size+=1
            else:
                raise ValueError('to much root')
        return tmp

    def dump(self,parent=None,index=1):
        if parent is None:
            parent=self.root
            if self.root is not None:
                print(self.root.element())
        if self.root is not None:
            childrens=self.childrens(parent)
            for children in childrens:
                print('  '*index,children.element())
                if len(self.childrens(children))>0:
                    self.dump(parent=children,index=index+1)
        else:
            raise ValueError('empty')
        
        
