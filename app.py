from flask import Flask, request
from bs4 import BeautifulSoup as bs
import requests
import json
import time
import os

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_URL = 'https://api.hphk.io/telegram'


def master_key_info(cd):
    url = 'http://www.master-key.co.kr/booking/booking_list_new'
    params = {
                'date': time.strftime("%Y-%m-%d"),
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

def seoul_excape_list():
    total = get_total_info()
    return total.keys()
    
def seoul_escape_info(cd):
    total = get_total_info()
    cafe = total[cd]
    tmp = []
    for theme in cafe:
        tmp.append('{}\n{}'.format(theme['title'], '\n'.join(theme['info'])))
    return tmp
    
@app.route('/{}'.format(os.getenv('TELEGRAM_TOKEN')), methods=['POST'])
def telegram():
    #텔레그램으로부터 요청이 들어올 경우, 해당 요청을 처리하는 코드
    response = request.get_json()
    url = 'https://api.hphk.io/telegram/bot{}/sendMessage'.format(TELEGRAM_TOKEN)
    
    chat_id = response['message']['from']['id'] 
    msg = response['message']['text']
    
    if msg == '안녕':
        msg = '첫만남에는 존댓말을 해야죠'
    elif msg == '안녕하세요':
        msg = '인사잘하신다 ㅋㅋㅋㅋ'
    # 마스터키 전체
    # 마스터키 ****점
    elif(msg.startswith('마스터키')):
        cafe_name = msg.split(' ')[1]
        cd = cafe_list[cafe_name]
        if cd > 0:
            data = master_key_info(cd)
        else:
            data = master_key_list()
        msg = []
        for d in data:
            msg.append('\n'.join(d.values()))
        msg = '\n'.join(msg)    
    elif(msg.startswith('서이룸')):
        cafe_name = msg.split(' ')
        if(len(cafe_name)>2):
            cafe_name = ' '.join(cafe_name[1:3])
            data = seoul_escape_info(cafe_name)
            print(cafe_name)
        else:
            cafe_name = cafe_name[-1]
            if(cafe_name == '전체'):
                data = seoul_excape_list()
            else:
                data = seoul_escape_info(cafe_name)
        msg = '\n'.join(data)
    else:
        msg = '등록되지 않은 지점 입니다'
    requests.get(url, params ={"chat_id":chat_id, "text":msg})
    return '',200

def master_key():
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
    
    print(result)
    return result

def get_total_info():
    url = 'http://www.seoul-escape.com/reservation/change_date/'
    params = {
                'current_date' : '2018/12/21'
    }
    
    response = requests.get(url,params).text
    document = json.loads(response)
    cafe_code = {
        '강남1호점':3,
        '홍대1호점':1,
        '부산 서면점':5,
        '인천 부평점':4,
        '강남2호점':11,
        '홍대2호점':10
    }
    total = {}
    game_room_list = document['gameRoomList']
    #기본틀잡기
    for cafe in cafe_code:
        total[cafe] = []
        for room in game_room_list:
            if(cafe_code[cafe] == room['branch_id']):
                total[cafe].append({'title': room['room_name'], 'info': []})
    
    book_list = document['bookList']
    # 앞에서 만든 틀에 데이터 집어넣기
    for cafe in total:
        for book in book_list:
            if(cafe == book['branch']):
                for theme in total[cafe]:
                    if(theme['title'] == book['room']):
                        if(book['booked']):
                            booked = '예약완료'
                        else:
                            booked = '예약가능'
                        theme['info'].append('{} - {}'.format(book['hour'],booked))
    return total



    
@app.route('/set_webhook')
def set_webhook():
    url = TELEGRAM_URL + '/bot' + TELEGRAM_TOKEN + '/setWebhook'
    params = {
        'url': 'https://ssafy-week2-dongjunhyun.c9users.io/{}'.format(TELEGRAM_TOKEN)
    }
    response = requests.get(url, params = params).text
    print("찍힙니까?")
    return response


cafe_list={
    '전체' : -1,
    '부천점': 15,
    '안양점': 13,
    '대구동성로2호점': 14,
    '대구동성로점': 9,
    '궁동직영점': 1,
    '은행직영점': 2,
    '부산서면점': 19,
    '홍대상수점': 20,
    '강남점': 16,
    '건대점': 10,
    '홍대점': 11,
    '신촌점': 6,
    '잠실점': 21,
    '부평점': 17,
    '익산점': 12,
    '전주고사점': 8,
    '천안신부점': 18,
    '천안점': 3,
    '천안두정점': 7,
    '청주점': 4    
}