from bs4 import BeautifulSoup
import re
soup = BeautifulSoup(open('test.html','r',encoding='UTF-8'), 'html.parser')
res=soup.find_all('td','runtime')
#print(res)
print('0xb7')
#print(re.findall('href="(.*?)"',str))