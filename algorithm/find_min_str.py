from collections import defaultdict

def isTargetInSrcHash(targetHash,srcHash):
    pass

src='123fhsdkhvsjkfgheuioryg92834yfgsuivdfhb'
target='love'
start,end=0,0
targetHash=defaultdict(int)
srcHash=defaultdict(int)
for s in target:
    targetHash[s]=1

for start in range(len(src)):
    while end<len(src) and not isTargetInSrcHash(targetHash,srcHash):
        srcHash[src[end]]+=1
        end+=1
    if isTargetInSrcHash(targetHash,srcHash):
        
