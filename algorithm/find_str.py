str1='abcdefg'
offset_val=1
str_i='12345123456'
target='123456'
c=0
def find(src_str,target):
    global c
    rtv=-1
    s_map=[0]*len(src_str)
    for i in range(len(src_str)):
        c+=1
        if s_map[i]==1:
            #print('continue')
            continue 
        else:
            s_map[i]=1
            
        if src_str[i] == target[0]:
            rtv=i
            c+=1
            for j in range(1,len(target)):
                
                print(i+j,'=1')
                c+=1
                if src_str[i+j]==target[j]:
                    s_map[i+j]=1
                else:
                    rtv=-1
                    break
            if rtv != -1:
                break
    print(s_map)
    return rtv
        
r=find(str_i,target)    
