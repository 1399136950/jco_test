a=[1,2,3,4,5,6]
dp=[0]*(len(a)+1)
dp[0]=0
dp[1]=1
for i in range(2,len(a)):
    for j in range(1,i):
        if a[i]>a[j]:
            dp[i]=max(dp[i],dp[j]+1)
    
