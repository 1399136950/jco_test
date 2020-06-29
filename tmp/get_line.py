def get_line(point1,point2):
    x1,y1=point1
    x2,y2=point2
    b=(y2*x1-y1*x2)/(x1-x2)
    k=(y1-y2)/(x1-x2)
    print(k,b)
    point_lists=[]
    for i in range(min(x1,x2),max(x1,x2)+1):
        point_lists.append([i,k*i+b])
    return point_lists
    
