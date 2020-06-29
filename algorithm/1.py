left='({['
right=')}]'
str1='([{test(}])'
tmp=[]
for i in str1:
    if i in left:
        tmp.append(i)
    if i in right:
        if left.index(tmp.pop())==right.index(i):
            pass
        else:
            break
    print(i)
