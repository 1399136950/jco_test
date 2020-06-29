import requests
from time import sleep


url = 'http://192.168.201.205:554/'
for i in range(1000):
    try:
        r = requests.get(url)
    except:
        pass
    else:
        print(r.status_code)
        if r.status_code == 200:
            pass
        else:
            print(r.status_code)
            break
        sleep(1)
        r.close()
