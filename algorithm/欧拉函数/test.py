import sys


def get_d(φn,e):
    res=[]
    for i in range(1,10000):
        if (i*φn +1)%e == 0:
            res.append((i*φn +1)/e)
    return res


def euler(num):
    res = a = num
    for i in range(2, a):
        if i**2 > a:    # 当i的平方大于num就跳出
            break
        if a%i == 0:        
            res=res-res/i   # 如果a可以被i整除,那么所有是i的倍数的数字和num都有公约数i，所以这里要减去所有是i的倍数的数字的个数
            while a%i == 0:
                a/=i    # 从num中去除i因子
    if a > 1:
        res=res-res/a
    return int(res)

if __name__ == '__main__':
    m = 53
    n = 257
    e = 19
    dlist = get_d(euler(n),e)
    d = int(dlist[0])
    print('m: ',m)
    print('d: ',d)
    print('res: ',(m**(e*d))%n)
    c=m**e%n
    print('c: ', c)
    print('m: ', c**d%n)
