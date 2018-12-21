from bs4 import BeautifulSoup as bs
import requests

def master_key_info(cd):
    url = 'http://www.master-key.co.kr/booking/booking_list_new'
    params = {
                'date': '2018-12-21',
                'store': cd
             }
    response = requests.post(url, params).text
    document = bs(response,'html.parser')
    ul = document.select('.reserve .escape_view')
    theme_list = []
    
    for i in ul:
        title = i.select('p')[0].text
        info = ''
        for col in i.select('.col'):
            info = info + '{} - {}\n'.format(col.select_one('.time').text,col.select_one('.state').text)
        theme = {
                'title':title,
                'info':info
        }
        theme_list.append(theme)
    
    return theme_list
    
    
def master_key_list():
    url = 'http://www.master-key.co.kr/home/office'
    response = requests.get(url).text
    document = bs(response,"html.parser")
    ul = document.select('.escape_list .escape_view')
    
    result=[]
    for i in ul:
        title = i.select_one('p').text
        if(title.endswith('NEW')):
            title = title[:-3]
        
        cafe ={
                'title':title,
                'tel':i.select('dd')[1].text,
                'address':i.select('dd')[0].text,
                'link':'http://www.master-key.co.kr'+i.select_one('a')['href']
        }
        result.append(cafe)
        
    return result
    
# 사용자로부터 '마스터키 ****점' 이라는 메시지를 받으면

# 해당 지점에 대한 오늘의 정보를 요청하고(크롤링)

# 메시지(예약정보)를 보내준다.
    

for cafe in master_key_list():
    print('{}: {}'.format(cafe['title'],cafe['link'].split('=')[1]))

print(master_key_info(21))
