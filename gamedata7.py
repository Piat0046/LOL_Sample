import requests
import json
import time
import pprint
from urllib import parse
from tqdm import tqdm
pp = pprint.PrettyPrinter(indent=4)
request_header = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36",
                    "Accept-Language": "ko,en-US;q=0.9,en;q=0.8,es;q=0.7",
                    "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
                    "Origin": "https://developer.riotgames.com",
                    "X-Riot-Token": 'RGAPI-ef7f8cda-b5bf-472f-9c16-746901f4093b'  #jhpa0046
                }

def check(url):
    r = requests.get(url, headers=request_header)
    if r.status_code == 200: # response가 정상이면 바로 맨 밑으로 이동하여 정상적으로 코드 실행
        pass
    
    elif r.status_code == 429:
        print('api cost full : infinite loop start')
        start_time = time.time()
        
        while True: # 429error가 끝날 때까지 무한 루프
            if r.status_code == 429:

                print('try 10 second wait time')
                time.sleep(10)

                r = requests.get(url, headers=request_header)
                print(r.status_code)

            elif r.status_code == 200: #다시 response 200이면 loop escape
                print('total wait time : ', time.time() - start_time)
                print('recovery api cost')
                break

def save_mongo(name_str, data_name):
    from http import client
    from xml.dom.minidom import Document
    from pymongo import MongoClient
    import certifi
    
    ##몽고db 계정정보
    HOST = 'cluster0.l3phm.mongodb.net'
    USER = 'jhp0046'
    PASSWORD = 'qkrwlgns0046'
    DATABASE_NAME = 'myFirstDatabase'
    COLLECTION_NAME = name_str
    MONGO_URI = f"mongodb+srv://{USER}:{PASSWORD}@{HOST}/{DATABASE_NAME}?retryWrites=true&w=majority"
    ca = certifi.where()
    client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())

    db = client[DATABASE_NAME]
    col = db[COLLECTION_NAME]
    col.insert_one(data_name)

    
def gamedata(gameId):
    print(f'{gameId}의 데이터 수집을 시작합니다.')
    data_list = {}
    url = f"https://asia.api.riotgames.com/lol/match/v5/matches/{gameId}"
    check(url)
    data = requests.get(url, headers=request_header).json()
    
    if data['info']['teams'][0]['win'] == True:
        data_list[gameId] = data['info']['teams'][0]['teamId']
    else:
        data_list[gameId] = data['info']['teams'][1]['teamId']
                        
    for user_num in range(0,10):
        puuid = data['info']['participants'][user_num]['puuid']
        champ_name = data['info']['participants'][user_num]['championName']
        champ_id = data['info']['participants'][user_num]['championId']
        status_url = f"https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{parse.quote(puuid)}"
        check(status_url)
        status = requests.get(status_url, headers=request_header).json()
        champ_status_url = f"https://kr.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/{parse.quote(status['id'])}/by-champion/{champ_id}"
        check(champ_status_url)
        champ_status = requests.get(champ_status_url, headers=request_header).json()
        champ_point = champ_status['championPoints']
        data_list[champ_name] = [champ_point, champ_id]
    
    
    save_mongo('loldata' , data_list)
    
    return print(f'{gameId}의 데이터 수집이 완료되었습니다')


import sqlite3

conn = sqlite3.connect('loldata.db')
cur = conn.cursor()
gameId_list = [] 
for row in cur.execute("SELECT * FROM gameID ORDER BY gameid ASC"):
    gameId_list.append(str(row).split('\'')[1])

conn.commit()
cur.close
conn.close

for i in tqdm(gameId_list[50000:55000]):
    try:
        gamedata(i)
    except:
        pass