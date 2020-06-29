import math



def listappend(list1,list2):
	newlist=[]
	while 1:
		if len(list1)>0 and len(list2)>0:
			if list1[0] <= list2[0]:
				newlist.append(list1[0])
				del list1[0];
			else:
				newlist.append(list2[0])
				del list2[0];
		else:
			if len(list1)==0:
				newlist=newlist+list2
			elif len(list2)==0:
				newlist=newlist+list1
			break
	return newlist
		

def gbsort(list):
	y=len(lists)%2
	newlist=[]
	while 1:
		if len(list)>=2:
			if list[0]<=list[1]:
				newlist.append([list[0],list[1]])
			else:
				newlist.append([list[1],list[0]])
			del list[0]
			del list[0]
		elif len(list)==1:
			newlist.append([list[0]])
			del list[0]
		else:
			break
	return newlist
	
		
lists=[1,2,3,4,65,78,99,7,5,3,2,12,5]
print(gbsort(lists))