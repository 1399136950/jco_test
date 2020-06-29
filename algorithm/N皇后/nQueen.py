from copy import deepcopy
class Queen():
    def __init__(self,n):
        self.n=n
        self.insert_index=[]
        self.exit_flag=False
        self.count=0
        self.res=[]
        self.main()
        

    def isPlaceCanUse(self,j,k,chessboard,c):
        if j>=self.n or k >=self.n:
            return False
        else:
            if c[k]>0:
                return False
            else:
                index=[]
                if j-1>=0:
                    index.append([j-1,k])
                    if k-1>=0:
                        index.append([j-1,k-1])
                    if k+1<self.n:
                        index.append([j-1,k+1])
                for i in index:
                    if chessboard[i[0]][i[1]]=='Q':
                        return False
                return True
    
    def pop(self):
        if len(self.insert_index)==0:
            self.exit_flag=True
            print('exit')
            return False
        else:
            x,y=self.insert_index.pop()
            print(x,y,'pop')
            if x==0 and y==self.n-1:
                return False
            return [x,y]
            
    
    def init_chessboard(self):
        chessboard=[]
        for i in range(self.n):
            chessboard.append(['.']*self.n)
        return chessboard
    
    def main(self):
        j,k=0,0
        chessboard=self.init_chessboard()
        c=[0]*self.n
        while j<self.n and k < self.n:
            while not self.isPlaceCanUse(j,k,chessboard,c) and k<self.n:
                k+=1
            if k==self.n:#这一行找不到插入点
                print('Line : ',j,'cant not set')
                res=self.pop()
                if res:
                    x,y=res
                    chessboard[x][y]='.'
                    c[y]=0
                    while y+1>=self.n:
                        res=self.pop()
                        if res:
                            x,y=res
                            chessboard[x][y]='.' 
                            c[y]=0
                        else:
                            break
                    j,k=x,y+1

            if self.exit_flag==True:
                break
            else:
                if self.isPlaceCanUse(j,k,chessboard,c):
                    print(j,k,'set')
                    self.insert_index.append([j,k])
                    chessboard[j][k]='Q'
                    c[k]+=1
                    k=0
                    j+=1
                if c==[1]*self.n:
                    t=deepcopy(chessboard)
                    self.res.append(t)
                    for p in chessboard:
                        print(p)
                        
                    self.count+=1
                    res=self.pop()
                    if res:
                        x,y=res
                        chessboard[x][y]='.'
                        c[y]=0
                        while y+1==self.n:
                            res=self.pop()
                            if res:
                                x,y=res
                                chessboard[x][y]='.' 
                                c[y]=0
                            else:
                                break
                        j,k=x,y+1
                    else:
                        break

        print('count :',self.count)
                

                
                
a=Queen(6)
'''
fd=open('2.txt','a+')
for i in a.res:
    for j in i:
        s=''
        for k in j:
            s+=k
        s+='\r\n'
        fd.write(s)
    fd.write('\r\n\r\n')
fd.close()
'''
