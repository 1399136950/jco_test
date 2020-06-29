def match_str(src_str, dst_str):
    l = len(src_str)
    path = {}
    dst_len = len(dst_str)
    for i in range(dst_len):
        path[dst_str[i]] = i
    i = 0
    while i <= l-len(dst_str):
        rtv = True
        for j in range(dst_len-1, -1, -1):
            if dst_str[j] != src_str[i+j]:
                rtv = False
                if src_str[i+j] in dst_str:
                    i += j - path[src_str[i+j]] # 如果该字符串在匹配的字符串中,则
                else:
                    i += j+1 # 该字符串不在匹配的字符串中,则从下一个字符重新开始迭代
                break
        if rtv:
            return i
    return -1

if __name__ == '__main__':
    strs = 'hellasdijaisdjeoqisjgbzvcxhellooo'
    res=match_str(strs, 'hello')
    print(res)
    print(strs[res:])
