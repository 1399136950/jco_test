
def test():
    b = yield 'start'
    print(b)
    a = yield 'test'
    print(a)


async def a():
    await test()
# gen = test()
