li=[i for i in range(10000)]
def er_fen(target,start,end):
    if li[start]==target:
        return start
    else:
        index=int((start+end)/2)
        if li[index] < target:
            return er_fen(target,index,end)
        if li[index] == target:
            return index
        else:
            return er_fen(target,start,index)
        
l_len=len(li)-1
r=er_fen(8888,0,l_len)
        
