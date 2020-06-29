from collections import defaultdict
src='123loveurdfiosjdfgsjgsoivh98wehfskjdviakdhflovesjdfhvndxjyou'
target='helo'

for i in range(len(src)):
    if src[i] in target:
        targetHash=defaultdict(int)
        for ch in target:
            targetHash[ch]=0
        #targetHash[src[i]]=1
        start=i
        for j in range(i,len(src)):
            if src[j] in target:
                targetHash[src[j]]+=1
                rtv=True
                for key in targetHash:
                    if targetHash[key]>=1:
                        pass
                    else:
                        rtv=False
                if rtv:
                    end=j
                    break
        if rtv:
            break
print(src[start:end+1])
