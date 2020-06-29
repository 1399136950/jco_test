from random import randint
from time import time

lists=[]

for i in range(500000):
	lists.append(randint(1,1000))

def qsort(lists):
	list1=[]
	list2=[]

	if len(lists) == 1:
		return lists
	elif len(lists) == 0:
		return []
	else:
		for num in range(1,len(lists)):
			if lists[num] <= lists[0]:
				list1.append(lists[num])
			else:
				list2.append(lists[num])
		list1=qsort(list1)
		list2=qsort(list2)
		list1.append(lists[0])
		return list1+list2
		
def mysort(lists):
	for i in range(len(lists)):
		for j in range(i+1,len(lists)):
			if lists[j]>=lists[i]:
				pass
			else:
				tmp=lists[i]
				lists[i]=lists[j]
				lists[j]=tmp
	return lists	
start=time()	
#mysort(lists)
end=time()
print(round(end-start,5))
start=time()	
qsort(lists)
end=time()
print(round(end-start,5))