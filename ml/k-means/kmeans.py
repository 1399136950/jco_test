import numpy as np
from time import sleep
import matplotlib.pyplot as plt
import random
def get_centroid(lists):
    if len(lists)>0:
        x_count=0
        y_count=0
        for point in lists:
            x_count+=point[0]
            y_count+=point[1]
        return [x_count/len(lists),y_count/len(lists)]
    else:
        return [random.randint(0,x_max),random.randint(0,y_max)]

def get_distance(point_a,point_b):
    if len(point_a) ==len(point_b):
        count=0
        for i in range(len(point_a)):
            count+=(point_a[i]-point_b[i])**2
        return count**0.5
    else:
        return False
points=[]

for i in range(100):
    x=random.randint(66,100)
    y=random.randint(66,100)
    points.append([x,y])
x_max=0
y_max=0
for point in points:
    if point[0] > x_max:
        x_max=point[0]
    if point[1] > y_max:
        y_max=point[1]
class_a_point=[random.randint(0,x_max),random.randint(0,y_max)]
class_b_point=[random.randint(0,x_max),random.randint(0,y_max)]
class_c_point=[random.randint(0,x_max),random.randint(0,y_max)]
min_distance=0.1
while(True):
    class_a=[]
    class_b=[]
    class_c=[]
    for point in points:
        a_distance=((point[0]-class_a_point[0])**2+(point[1]-class_a_point[1])**2)**0.5
        b_distance=((point[0]-class_b_point[0])**2+(point[1]-class_b_point[1])**2)**0.5
        c_distance=((point[0]-class_c_point[0])**2+(point[1]-class_c_point[1])**2)**0.5

        min_value=min([a_distance,b_distance,c_distance])

        if min_value==a_distance:
            class_a.append(point)
        if min_value==b_distance:
            class_b.append(point)
        if min_value==c_distance:
            class_c.append(point)
            
            

    class_a_point_bf=class_a_point
    class_b_point_bf=class_b_point
    class_c_point_bf=class_c_point
    class_a_point=get_centroid(class_a)
    class_b_point=get_centroid(class_b)
    class_c_point=get_centroid(class_c)
    print(class_a_point,class_b_point,class_c_point)


    for poing in class_a:
        plt.scatter(poing[0],poing[1],c = 'r',marker='.')
    for poing in class_b:
        plt.scatter(poing[0],poing[1],c = 'b',marker='.')
    for poing in class_c:
        plt.scatter(poing[0],poing[1],c = 'k',marker='.')
    plt.scatter(class_a_point[0],class_a_point[1],marker='+',c = 'r')
    plt.scatter(class_b_point[0],class_b_point[1],marker='+',c = 'b')
    plt.scatter(class_c_point[0],class_c_point[1],marker='+',c = 'k')
    plt.show()

    if get_distance(class_a_point_bf,class_a_point)<min_distance and get_distance(class_b_point_bf,class_b_point)<min_distance and get_distance(class_c_point_bf,class_c_point)<min_distance:
        print('ok')
        break



    
