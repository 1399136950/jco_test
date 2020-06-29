import numpy as np
str1='abc'
str2='abc'
dp=np.zeros([len(str1)+1,len(str2)+1])
for i in range(1,len(str1)+1):
    for j in range(1,len(str2)+1):
        if str1[i-1]==str2[j-1]:
            dp[i][j]=dp[i-1][j-1]+1
        else:
            dp[i][j]=max(dp[i-1][j],dp[i][j-1])
        
