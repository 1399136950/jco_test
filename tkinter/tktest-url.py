from threading import Thread
from tkinter import *
from time import sleep,ctime,time
from queue import Queue 
import random
import math
import re
import requests
#from io import BytesIO

class MainWindow:
	exitflag=1
	threadnum=6
	
	def __init__(self):
		self.frame = Tk()
		
		
		self.label_urlname = Label(self.frame,text = "url:")
		self.thread_num = Label(self.frame,text = "progessbar:")

		#self.text_urlname = Text(self.frame,height = "1",width = 30)
		self.text_urlname = Entry(self.frame, width="50")

		
		self.button_ok = Button(self.frame,text = "start",width = 10)
		self.button_ok.bind("<ButtonPress>",self.buttonclick)
		
		self.button_cancel = Button(self.frame,text = "stop",width = 10)
		self.button_cancel.bind("<ButtonPress>",self.buttoncancle)
		
		self.scale=Scale(self.frame,from_=0,to=100,resolution=1,orient=HORIZONTAL,length=216)
		self.scale.set(0)

		self.label_urlname.grid(row = 0,column = 0)
		self.thread_num.grid(row = 1,column = 0)
	
		self.button_ok.grid(row = 3,column = 0)

		self.text_urlname.grid(row = 0,column = 1)
		self.scale.grid(row = 1,column = 1)
	
		self.button_cancel.grid(row = 3,column = 1)
		
		self.text=Text(self.frame)
		self.text.grid(rows=4,columnspan=2)
		
		self.frame.mainloop()
	
	def buttoncancle(self,event):
		self.exitflag=0
		print('[buttoncancle]: set exitflag 0')
	
	
	def buttonclick(self,event):
		self.exitflag=1
		if self.scale.get()>1 and self.scale.get()<100:
			print('no')
			self.text.insert(END,"alredy running\r\n")
		else:
			Thread(target=self.mythread).start()
			
			
	
	def mythread(self):
		'''file=open('test.html',encoding='utf-8')
		str=file.read()
		file.close()'''
		self.scale.set(0)
		url=self.text_urlname.get()
		str=self.getHtml(url)
		#rule='\<img.*?src="(http\:\/\/.*?\.jpg)".*?\>'
		httptype=url.split('://')[0]
		name=url.split('://')[1].split('/')[0]
		hostname=httptype+'://'+name
		if str:
			#rule='\<img.*?src="((?:(?:http|https)\:\/\/){0,1}.*?\.(?:jpg|png|jpeg|gif))".*?\>'
			rule='\<a.*?href="(.*?)".*?\>(.*?)\</a\>'
			#rule='\<a.*?\>(.*?)\</a\>'
			res=re.findall(rule,str)
			res=list(set(res))
			self.q=Queue(0)
		
			for i in range(len(res)):
				
				self.q.put(res[i])
	
			
			self.qlen=self.q.qsize()
			Thread(target=self.setscale).start()
			
			self.text.insert(END,"start\r\n")
			sleep(1)
			start=ctime()
			threads=[]
			for i in range(self.threadnum):
				thread=Thread(target=self.dosomething,args=(i,hostname))
				threads.append(thread)
			for thread in threads:
				thread.start()
			for thread in threads:
				thread.join()
			self.text.insert(END,"finished\r\n")
			print(start)
			print(ctime())
			print('finished')
			self.scale.set(100)
		else:
			print("cant't get html")
			
	
	def getHtml(self,url):
		try:
			html=requests.get(url)
		except requests.exceptions.ConnectionError:
			print('error')
			return False
		else:
			print(html.status_code)
			#print(html.heards)
			return html.text
	
	def setscale(self):
		while 1:
			if self.q.empty() or self.exitflag==0:
				print('[setscale]:exitflag = 0,exit now')
				break
			else:
				progess=(1-self.q.qsize()/self.qlen)*100
				self.scale.set(math.ceil(progess))
				sleep(0.1)
	
	def getimg(self,imgurl,localname,hostname):
		#headers = {"Referer": 'http://www.meituri.com/',"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0"}
		headers = {"referer": 'http://tieba.baidu.com/',"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0"}
		if len(re.findall('(?:http|https)\:\/\/.*?',imgurl))==0:#with not https:// or http://
			if len(re.findall('^//{2}.*?$',imgurl)) == 0:
				if len(re.findall('^/{1}.*?$',imgurl)) > 0:
					imgurl=hostname+imgurl
				elif len(re.findall('^(?:[0-9]|[a-z]|[A-Z]).*?$',imgurl)) > 0:
					imgurl=hostname+'/'+imgurl
			else:
				imgurl='http:'+imgurl
		img=requests.get(imgurl,headers=headers)
		image=img.content
		f = open('test/'+localname,'wb')
		f.write(image)
		f.close()
		sleep(1)
		
	def dosomething(self,i,hostname):
		while 1:
			if self.exitflag:
				if not self.q.empty():
					imgurl=self.q.get()
					print('thread [{}] :get'.format(i),imgurl)
					#local="{}".format(random.randint(1,999))+"{}.".format(time())+imgurl.split('.')[-1]
					#self.getimg(imgurl,local,hostname)
					f=open('1.txt',mode='a+')
					f.write(imgurl[0]+"\r\n"+imgurl[1]+"\r\n\r\n")
					f.close()
					sleep(0.5)
	
				else:
					print('thread [{}] :empty queue,exit now'.format(i))
					break
			else:
				print("thread [{}] :killed".format(i))
				break;
		if self.exitflag:
			#self.text.insert(END,"exit\r\n")
			pass
		else:
			self.text.insert(END,"killed\r\n")
		
 
frame = MainWindow()