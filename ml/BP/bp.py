import numpy as np
from  matplotlib import pyplot as plt 
def logsig(num):
    tmp= 1/(1+1/np.exp(num))
    return tmp    
def d_logsig(num):
    return logsig(num)*(1-logsig(num))

class MyBp():
    def __init__(self):
        self.err=1
        self.learning_rate=0.6
        self.input_count=2
        self.hidden_count=2
        self.res_count=1
        self.input_w=np.array([[0.1,0.4],[-0.2,0.2]])
        self.hidden_w=np.array([[0.2],[-0.5]])
        
    def get_hidden(self,input_list,hidden_index):
        res=0
        for i in range(len(input_list)):
            res=res+input_list[i]*self.input_w[i][hidden_index]
        return logsig(res)
        
    def get_output(self,hidden_input_lists):
        res=0
        for i in range(len(hidden_input_lists)):
            res=res+hidden_input_lists[i]*self.hidden_w[i][0]
        return logsig(res)
    
    def get_err_value(self,value1,value2):
        return (value1-value2)**2
    
    def learn(self,input_list,value):
        hidden_list=[]
        for i in range(self.hidden_count):
            hidden_list.append(self.get_hidden(input_list,i))
        res=self.get_output(hidden_list)
        self.err=self.get_err_value(res,value)
        error_term_output=self.get_error_term_from_output(res,value)
        error_term_hidden=self.get_error_term_from_hidden(error_term_output,hidden_list)
        #更新input->hidden的权重
        for i in range(len(input_list)):
            for j in range(self.hidden_count):
                tmp=input_list[i]*error_term_hidden[j]*self.learning_rate
                self.input_w[i][j]=self.input_w[i][j]+tmp
        #更新hidden->output的权重
        for i in range(self.hidden_count):
            tmp=hidden_list[i]*error_term_output*self.learning_rate
            self.hidden_w[i][0]=self.hidden_w[i][0]+tmp
        #print('input:\t',input_list)
        #print('hidden:\t',hidden_list)
        #print('output:\t',res)
        #print('err:\t',self.err)
        #print('error_term_output\t',error_term_output)
        #print('error_term_hidden\t',error_term_hidden)
        #print('input_w\t',self.input_w)
        #print('hidden_w\t',self.hidden_w)
    
    def get_error_term_from_output(self,res,value):
        return -(res-value)*res*(1-res)
        
    def get_error_term_from_hidden(self,error_term_output,hidden_list):
        res=[]
        for i in range(self.hidden_count):
            tmp=error_term_output*self.hidden_w[i][0]*hidden_list[i]*(1-hidden_list[i])
            res.append(tmp)
        return res
    
    def calculate(self,input_list):
        hidden_list=[]
        for i in range(self.hidden_count):
            hidden_list.append(self.get_hidden(input_list,i))
        res=self.get_output(hidden_list)
        print(res)

a=MyBp()
test_data=[
    [1,2],
    [0.3,5],
    [0.6,1],
    [0.2,4],
    [0.1,2],
    [2,2],
    [1,0.3],
    [0.4,5]
]



test_res=[2,1.5,0.6,0.8,0.2,4,0.3,2]


while 1:
    for i in range(len(test_res)):
        a.learn(test_data[i],test_res[i])
        print(a.err)
        if a.err<0.001:
            break
    if a.err<0.001:
        break
