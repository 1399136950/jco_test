from matplotlib import pyplot as plt
def draw(n):
    l=[i for i in range(n,6*n+1)]
    count={}
    for num in l:
        count[str(num)]=0
    for i in range(1,6+1):
        for j in range(1,6+1):
            for k in range(1,6+1):
                for m in range(1,6+1):
                    res=i+j+k+m
                    count[str(res)]+=1
    print(count)
    x=l
    y=[]
    for i in l:
        y.append(count[str(i)])
    plt.scatter(x,y)
    plt.show()
draw(4)
