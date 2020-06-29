def test():
    count = 0
    nums = 0
    def averange(val):
        nonlocal count
        nonlocal nums
        count += val
        nums += 1
        return count/nums
    return averange





a=test()
print(a(10))
print(a(2))
