from regiongrow import Regiongrow
import os

class Analysis_identifying_code():
    
    def __init__(self):
        self.regiongrow=Regiongrow()
    
    def handle_image(self,src,dist):
        self.regiongrow.load_img(src)
        self.regiongrow.main()
        self.regiongrow.save_img(dist)
    
    #分类图片
    def classify_image(self,img):
        pass
    
    #学习
    def training(self):
        pass
    
    #测试
    def testing(self):
        pass

    def mkdir(self):
        if not os.path.exists('res/'):
            os.mkdir('res')
            for i in range(10):
                os.mkdir('res/'+str(i))
            str1='abcdefghijklmnopqrstuvwxyz'
            STR1=str1.upper()
            for tmp in str1:
                os.mkdir('res/'+tmp)
