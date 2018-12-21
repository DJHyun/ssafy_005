import requests
from bs4 import BeautifulSoup as bs

url = 'http://www.seoul-escape.com/contact/'
    
response = requests.get(url).text
document = bs(response,'html.parser')
tit = document.select('.branches a')
add = document.select('.branch_tab ul')
result =[]
print(add)
add = ''.join(add.text)
print(add)
for i in tit:
    for j in add:
        cafe={
            'title': i.text,
            'address' : j.text
        }
    result.append(cafe)
print(result)