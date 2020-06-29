from sklearn import datasets                            #引入数据集,sklearn包含众多数据集 
from sklearn.model_selection import train_test_split    #将数据分为测试集和训练集 
from sklearn.neighbors import KNeighborsClassifier      #利用邻近点方式训练数据 ###引入数据### 

X_train=[]
Y_train=[]
file=open('data.txt','r')
lines=file.readlines()

for i in range(len(lines)):
    tmp=lines[i].strip('\n').split('\t')
    X_train.append(tmp[0:3])
    Y_train.append(tmp[-1])
knn=KNeighborsClassifier()  #引入训练方法 
knn.fit(X_train,Y_train)    #进行填充测试数据进行训练

file1=open('tmp.txt','r')
lines1=file1.readlines()
X_test=[]
Y_test=[]

for i in range(len(lines1)):
    tmp=lines[i].strip('\n').split('\t')
    X_test.append(tmp[0:3])
    Y_test.append(tmp[-1])
res_test=knn.predict(X_test) #预测特征值 

num=0

for j in range(len(res_test)):
    if res_test[j]==Y_test[j]:
        num+=1
        print(res_test[j],Y_test[j],'true')
    else:
        print(res_test[j],Y_test[j],'false')

print('准确率:',100*num/len(Y_test))

