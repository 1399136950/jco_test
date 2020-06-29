def merge_sort(l):
    '''
    length = 1
    i = 0
    size = len(l)
    while i < size-1:
        if l[i+1] < l[i]:
            l[i],l[i+1] = l[i+1],l[i]
        i += 2
    '''
    size = len(l)
    length = 1
    start1 = 0
    while start1 < size:
        start2 = start1 + length
        if start2 >= size:
            start2 = size - 1
        merge_partition(l, start1, start2, length) 
        start1 += length 

    # length = length*2


def merge_partition(l, start1, start2, length):
    for i in range(start2, start2+length):
        val = l[i]
        j = i - 1
        while j >= start1 and l[j] > val:
            l[j+1] = l[j]
            j -= 1
        l[j+1] = val
        
if __name__ == '__main__':
    l = [2,34,3,53,3,47,678,67,86,9,56,73,45,23,42,35,546,457,68,67,8,3,4]
    # l = [1,34,56,72,678,5,8,546,4333,34567,234,23,434,65,578,679,9,8,8,9,67,546,456]
    # merge_partition(l, 0, 5 , 5)
    merge_sort(l)
    print(l)
