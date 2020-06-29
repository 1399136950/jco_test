

def partition(l, s, e):
    val = l[e]
    i = s - 1
    for j in range(s, e):
        if l[j] < val:
            i += 1
            l[i],l[j] = l[j],l[i] 
    l[i+1],l[e] = l[e],l[i+1]
    return i+1
    


def qsort(l, s, e): # 递归版本
    if e > s and s >=0:
        res=partition(l, s, e)
        qsort(l,s,res-1)
        qsort(l,res+1,e)
        
def qsort1(l): # 迭代版本
    pass
        
l = [12,3,324,435,44,467,56,78,768,5,67,45,64,5,3,45,3,234,23,4,435,4,1,312,3,26,78,989,678,456,3,34523,45,34,53]
qsort(l,0,len(l)-1)
