import sys

l=[2,6,-3,5,6,-20,34]
dp=[0]*len(l)
dp[0]=l[0]
for i in range(1,len(l)):
    dp[i]=max(dp[i-1]+l[i],l[i])
    
