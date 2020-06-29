list=[1,2,3,4,5,5,4,5,6,72,4,6,1]

'''for j in range(1,len(list)):
	for i in range(len(list)-j):
		if list[i]>list[i+1]:
			tmp=list[i]
			list[i]=list[i+1]
			list[i+1]=tmp
		
print(list)'''

for i in range(len(list)):
	min=i
	for j in range(i+1,len(list)):
		if list[j]<list[min]:
			min=j
	if i==min:
		pass
	else:
		tmp=list[i]
		list[i]=list[min]
		list[min]=tmp
	print(list[i])
print(list)
			