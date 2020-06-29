import os
import cv2
from sklearn import datasets                            #引入数据集,sklearn包含众多数据集 
from sklearn.model_selection import train_test_split    #将数据分为测试集和训练集 
from sklearn.neighbors import KNeighborsClassifier      #利用邻近点方式训练数据 ###引入数据### 
from sklearn.externals import joblib
import numpy as np
from time import time
from regiongrow import Regiongrow


def get_feature(img):
    line,column=img.shape
    tmp_data=[]
    pix_count=0
    for i in range(line):
        pix_line_count=0
        for pix in img[i]:
            if pix == 0:
                pix_line_count+=1
            tmp_data.append(pix_line_count)
        pix_count+=pix_line_count
    img1=img.T
    for i in range(column):
        pix_column_count=0
        for pix in img1[i]:
            if pix == 0:
                pix_column_count+=1
            tmp_data.append(pix_column_count)
    tmp_data.append(pix_count)
    return tmp_data

if os.path.exists('code.pkl'):
    knn=joblib.load('code.pkl')
    print('exists')
else:
    #训练
    root_dir='res/'
    lists=os.listdir('res')
    learn_data=[]
    res_data=[]
    for name in lists:
        print(name)
        tmp=os.listdir('res/'+name)
        for file in tmp:
            img_path='res/'+name+'/'+file
            img=cv2.imread(img_path,0)
            line,column=img.shape
            tmp_data=[]
            pix_count=0
            for i in range(line):
                pix_line_count=0
                for pix in img[i]:
                    if pix == 0:
                        pix_count+=1
                        pix_line_count+=1
                    tmp_data.append(pix_line_count)
            img1=img.T
            for i in range(column):
                pix_column_count=0
                for pix in img1[i]:
                    if pix == 0:
                        pix_column_count+=1
                    tmp_data.append(pix_column_count)
            tmp_data.append(pix_count)
            learn_data.append(tmp_data)
            res_data.append(name)
    print('start train')
    knn=KNeighborsClassifier()  #引入训练方法 
    knn.fit(learn_data,res_data)
    print('finished')
    joblib.dump(knn,'code.pkl')
    
x_test=[]
y_test=[]

test_files=os.listdir('test')
a=Regiongrow()
for file in test_files:
    #****************处理图像****************#
    a.load_img('test/'+file)
    a.main()
    img1=a.img_th
    #***************提取特征值***************#
    name=file.split('.')[0]
    for i in range(1,5):
        tt=img1[0:,(i-1)*20:i*20]
        fea=get_feature(tt)
        x_test.append(fea)
        y_test.append(name[i-1])
        
start=time()
res_test=knn.predict(x_test)
end=time()
print(end-start)
index=0
count=0
for i in range(len(res_test)):
    count+=1
    if res_test[i].upper()==y_test[i].upper():
        index+=1
    else:
        pass
    print(res_test[i],y_test[i])
print('count:',count,'true:',index,'准确率:',index/count)


