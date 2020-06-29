import requests
import json

url = 'http://jco.linkpai.com/admin.php/admin/equipment/index.html?page=1&limit=1'

cookies = {
    'PHPSESSID':'ep065qcccdukjkte39rj345k46'
}

headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'http://jco.linkpai.com/admin.php/admin/equipment/index.html'
}

r = requests.get(url, cookies=cookies,headers=headers)

a=json.loads(r.text)

for info in a['data']:

    for key in info:
        print('{:<15} : {}'.format(key, info[key]))
    print('*'*50)
