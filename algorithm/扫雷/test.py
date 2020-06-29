map1=[[0,0,0],[0,0,1],[0,1,'']]

def find_flag(l,c):
    lists=[
        [l-1,c-1],
        [l-1,c],
        [l-1,c+1],
        [l,c-1],
        [l,c+1],
        [l+1,c-1],
        [l+1,c],
        [l+1,c+1]
    ]
    res=[]
    for i in lists:
        if i[0]>=0 and i[0]<lines:
            if i[1]>=0 and i[1]<columns:
                res.append(i)
    print(res)

lines=len(map1)
columns=len(map1[0])
for line in range(lines):
    for column in range(columns):
        if type(map1[line][column])==int:
            print(map1[line][column])
            find_flag(line,column)
