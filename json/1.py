import json
import os
dir1={'name':"徐军"}
with open('1.txt','a') as file:
    json.dump(dir1,file,indent=4,ensure_ascii=False)
