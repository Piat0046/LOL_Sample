from tracemalloc import stop
import requests
import json
import time
import pprint
import pandas as pd
from urllib import parse
pp = pprint.PrettyPrinter(indent=4)
request_header = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36",
                    "Accept-Language": "ko,en-US;q=0.9,en;q=0.8,es;q=0.7",
                    "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
                    "Origin": "https://developer.riotgames.com",
                    "X-Riot-Token": 'RGAPI-73e288ef-e47e-4716-a487-13c0df8f9c8e'
                }

# for문 진행률 확인 라이브러리
from tqdm import tqdm

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

def check2(url):
    r = requests.get(url, headers=request_header)
    if r.status_code == 200: # response가 정상이면 바로 맨 밑으로 이동하여 정상적으로 코드 실행
        m = 'pass'
        pass
    elif r.status_code == 403:
        m = 'pass'
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
                m = 'pass'
                break

            else:
                m = 'fail'
                break
    
    else:
        m = 'fail'
    return m

nick = 'DRX 홍창현'.replace(" ", "")
url_nick = f'https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/{parse.quote_plus(nick)}'
m = check2(url_nick)
if m == 'fail':
    m = '소환사를 찾을 수 없습니다.'
    print('소환사를 찾을 수 없습니다.')

elif m == 'pass':
    nick_to_id = requests.get(url_nick, headers=request_header).json()
    input_id = nick_to_id['id']

    url_game = f'https://kr.api.riotgames.com/lol/spectator/v4/active-games/by-summoner/{input_id}'
    m = check2(url_game)
    
    if m == 'fail':
        m = '소환사가 게임중이 아닙니다'
        print('소환사가 게임중이 아닙니다')

    elif m == 'pass':

        data = requests.get(url_game, headers=request_header).json()

        dic = []
        for i in range(0,10):
            summoner_Id = data['participants'][i]['summonerId']
            dic.append(summoner_Id)
        print(dic)

        dic = []

        for i in range(0,10):
            champ_id = data['participants'][i]['championId']
            summoner_Id = data['participants'][i]['summonerId']
            champ_status_url = f"https://kr.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/{summoner_Id}/by-champion/{champ_id}"
            m = check2(champ_status_url)
            print(m)
            champ_status = requests.get(champ_status_url, headers=request_header).json()
            champ_point = champ_status['championPoints']
            dic.append(champ_id)
            dic.append(champ_point)

        from flask import Flask, render_template, request
        import pickle
        import sqlite3
        import pandas as pd
        from xgboost import XGBClassifier
        #def create_app():

        app = Flask(__name__)

        model = None

        with open('model4.pkl', 'rb') as file:
            model = pickle.load(file)

        columns = ['1', '1score', '2', '2score', '3', '3score', '4', '4score', '5', '5score', '6', '6score', '7', '7score', '8', '8score', '9', '9score', '10', '10score']
        df = pd.DataFrame(columns = columns)
        input_data = {
                    '1' : dic[0],
                    '1score' : dic[1],
                    '2' : dic[2],
                    '2score' :dic[3],
                    '3' : dic[4],
                    '3score' : dic[5],
                    '4' : dic[6],
                    '4score' : dic[7],
                    '5' : dic[8],
                    '5score' : dic[9],
                    '6' : dic[10],
                    '6score' : dic[11],
                    '7' : dic[12],
                    '7score' : dic[13],
                    '8' : dic[14],
                    '8score' : dic[15],
                    '9' : dic[16],
                    '9score' : dic[17],
                    '10' : dic[18],
                    '10score' : dic[19],
                    }
        X_test = df.append(input_data, ignore_index=True)
        X_test = X_test.astype(int)
        y_pred = list(model.predict(X_test))[0]
        c=model.predict_proba(X_test).reshape(-1,1)

        if y_pred == 200:
            y_pred = '레드팀'
        else:
            y_pred = '블루팀'

        print(f'예상승리팀={y_pred}, 예상 확률 블루팀={int(list(c[0])[0]*100)}%, 레드팀{int(list(c[1])[0]*100)}% ')