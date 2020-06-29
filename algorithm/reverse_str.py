def reverse_str(src,start,end):
    if start==end or start > end:
        return True
    src[start],src[end]=src[end],src[start]
    reverse_str(src,start+1,end-1)    

src='hello world '
l=list(src)
length=len(l)-1
reverse_str(l,0,length)
