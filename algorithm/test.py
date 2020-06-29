def tree_height():
    q = Queue()
    count = 0
    next_count = 1
    tree_height = 0
    while q.qsize() > 0
        e = q.get()
        count += 1
        c = [e._left, e._right]
        for child in c:
            if c != None:
                q.put(c)

        if count == next_count:
            count = 0
            next_count = q.qsize()
            tree_height += 1
    return tree_height
