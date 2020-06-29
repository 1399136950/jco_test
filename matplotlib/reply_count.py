import matplotlib.pyplot as plt
import numpy as np
import datetime
from mydb import MyDb


a = MyDb('think_content')

b = a.select('content_time')

date_count = {}

date_count[2017] = {12:0}
date_count[2018] = {1:0,2:0,3:0,4:0,5:0,6:0,7:0,8:0,9:0,10:0,11:0,12:0}
date_count[2019] = {1:0,2:0,3:0,4:0,5:0,6:0,7:0,8:0,9:0,10:0,11:0,12:0}

for i in b:
    date_count[i[0].year][i[0].month] += 1

x=[]
y=[]

for year in date_count:
    for month in date_count[year]:
        y.append(date_count[year][month])
        x.append(str(year)+'-'+str(month))


plt.bar(x,y,width=0.4)
plt.title('reply count')
plt.show()
    
