def fast_pow(a,b,c):
    ans = 1
    a = a%c
    while b!=0:
        if b & 1:
            ans=(ans*a)%c
        b >>= 1
        a = (a*a)%c
    return ans

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
    
def encrypt(l, n, d):
    res = []
    for i in l:
        # res.append(i**d%n)
        res.append(fast_pow(i, d, n))
    return res

def decrypt(l, n, e):
    res = []
    for i in l:
        # res.append(i**e%n)
        res.append(fast_pow(i, e, n))
    return res



if __name__ == '__main__':
    p = 53
    q = 257
    n = p*q
    φ= (p-1)*(q-1)
    e = 47
    dlist = get_d(φ,e)
    d = int(dlist[0])
    pu = [n, e] # 公钥
    pr = [n, d] # 私钥
    m = b'hello world'  # 待加密数据
    en_res = encrypt(m, n, d) # 密文
    print(en_res)
    de_res = decrypt(en_res, n, e)  # 解密后的数据
    print(de_res)
    
