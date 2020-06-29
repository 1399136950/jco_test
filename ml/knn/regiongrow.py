import cv2
import numpy as np

class Regiongrow:

    def load_img(self,img_path):
        img=cv2.imread(img_path,0)
        h,w=img.shape
        img=img[1:h-1,1:w-1]
        rt,self.img_th=cv2.threshold(img,225,255,cv2.THRESH_BINARY)
        self.h1,self.w1=self.img_th.shape
        self.img_map=np.zeros([self.h1,self.w1],int)#初始化地图
    
    def get_around_point(self,l,c):
        tmp=[]
        points=[[l+1,c],[l-1,c],[l,c+1],[l,c-1]]
        for p in points:
            try:
                self.img_th[p[0]][p[1]]
            except:
                pass
            else:
                if self.img_map[p[0]][p[1]]==1:
                    pass
                else:
                    if self.img_th[p[0]][p[1]] == 0:
                        self.img_map[p[0]][p[1]]=1
                        tmp.append([p[0],p[1]])
        return tmp
        
    def main(self):
        for l in range(self.h1):
            for c in range(self.w1):
                if self.img_map[l][c]==1:
                    pass
                else:
                    self.img_map[l][c]=1
                    if self.img_th[l][c]==0:
                        res=[]
                        res.append([l,c])
                        li=self.get_around_point(l,c)
                        res.extend(li)
                        while True:
                            pre_len=len(res)
                            for i in res:
                                lists=self.get_around_point(i[0],i[1])
                                res.extend(lists)
                            post_len=len(res)
                            if post_len==pre_len:
                                break
                        if len(res)<=6:
                            for point in res:
                                self.img_th[point[0]][point[1]]=255
                                
    def save_img(self,path):
        cv2.imwrite(path,self.img_th)
                        