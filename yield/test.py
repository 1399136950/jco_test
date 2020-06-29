def average():
    global count
    while 1:
        a = yield
        if a == None:
            break
        count += a
    return count


def proxy_gen():
    while 1:
        res = yield from average()
        return res


def main():
    gen = proxy_gen()
    next(gen)
    for i in range(101):
        gen.send(i)
    try:
        res = gen.send(None)
    except Exception as e:
        print('err')
        res = e.value
    print(res)


if __name__ == '__main__':
    count = 0
    main()
