a=[
    [1,2,3],
    [1,56,6],
    [4,1,45],
    [99,456,999],
    [1,1,1],
    [12,31,34],
    [123,23,4532]
]
m,n=len(a),len(a[0])
dp=[[0]*n for i in range(m)]
dp[0][0]=a[0][0]
for i in range(m):
    for j in range(n):
        if i==j and i==0:
            pass
        else:
            if i-1>=0 and j-1 >=0:
                dp[i][j]=a[i][j]+min(dp[i-1][j],dp[i][j-1])
            else:
                if i-1<0:
                    dp[i][j]=a[i][j]+dp[i][j-1]
                elif j-1<0:
                    dp[i][j]=a[i][j]+dp[i-1][j]
