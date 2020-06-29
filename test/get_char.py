import requests
from bs4 import BeautifulSoup as bs

url = 'http://www.aies.cn/{}.htm'


l = 'abcdefghijklmnopqrstuvwxyz'
fd = open('1.txt', 'a+')
for i in l :
    new_url = url.format(i)
    print(new_url)
    r=requests.get(new_url)
    r.encoding='gbk'
    soup = bs(r.text, 'html.parser')
    string = soup.find_all('p','is-3')[1].get_text()
    l = string.split(' ')
    for s in l:
        fd.write(s)
fd.close()
