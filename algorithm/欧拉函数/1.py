

num = 16
a = num

for i in range(2, num):
    if i**2 > num:
        break
    if a%i == 0:    # 如果num可以被i整除,那么所有i的倍数和num都有公约数，所以这里要减去i的倍数的个数
        a = a - a/i
        while a%i == 0:
            a/=i
