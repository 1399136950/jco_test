def get_max_num(l):
    max_n = l[0]
    for i in l:
        if i > max_n:
            max_n = i
    return max_n

def count_sort(l):
    max_n = get_max_num(l)
    assist_l = [0] * (max_n+1)
    res = [None]*len(l)
    for j in l:
        assist_l[j] += 1
    index = 0
    for m in range(len(assist_l)):
        while assist_l[m] > 0:
            res[index] = m
            index += 1
            assist_l[m] -= 1
    return res

if __name__ == '__main__':
    l = [12,3,23,4,5,6,7,9,0,5,3,12,21,19,3,4,5,6,7,8,9,7,5,4,2,3,17,6,7,8,6,15]
    print(l)
    res = count_sort(l)
    print(res)
