from http import client
from xml.dom.minidom import Document
from pymongo import MongoClient
import certifi
import pandas as pd

col = ['gameid','win_team','1','1score','2','2score','3','3score','4','4score','5','5score','6','6score','7','7score','8','8score','9','9score','10','10score']
learn_data = pd.DataFrame(columns = col)

##몽고db 계정정보
HOST = 'cluster0.l3phm.mongodb.net'
USER = 'jhp0046'
PASSWORD = 'qkrwlgns0046'
DATABASE_NAME = 'myFirstDatabase'
COLLECTION_NAME = 'loldata'
MONGO_URI = f"mongodb+srv://{USER}:{PASSWORD}@{HOST}/{DATABASE_NAME}?retryWrites=true&w=majority"
ca = certifi.where()

client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())

db = client[DATABASE_NAME]

col = db[COLLECTION_NAME]

doc = col.find({})

game_data = []

for i in doc:
    game_data.append(i)

game_data = game_data[95:]

import sqlite3

conn = sqlite3.connect('loldata.db') # 데이터 베이스 생성
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS Match_data;")

cur.execute(f"""CREATE TABLE Match_data (
                "Id" INTEGER NOT NULL PRIMARY KEY,
                "gameid" NVARCHAR(160) NOT NULL,
                "win_team" NVARCHAR(160) NOT NULL,
                "1pick" INTEGER NOT NULL,
                "1score" INTEGER NOT NULL,
                "2pick" INTEGER NOT NULL,
                "2score" INTEGER NOT NULL,
                "3pick" INTEGER NOT NULL,
                "3score" INTEGER NOT NULL,
                "4pick" INTEGER NOT NULL,
                "4score" INTEGER NOT NULL,
                "5pick" INTEGER NOT NULL,
                "5score" INTEGER NOT NULL,
                "6pick" INTEGER NOT NULL,
                "6score" INTEGER NOT NULL,
                "7pick" INTEGER NOT NULL,
                "7score" INTEGER NOT NULL,
                "8pick" INTEGER NOT NULL,
                "8score" INTEGER NOT NULL,
                "9pick" INTEGER NOT NULL,
                "9score" INTEGER NOT NULL,
                "10pick" INTEGER NOT NULL,
                "10score" INTEGER NOT NULL               
                )
                ;""")

conn.commit()
cur.close
conn.close
from tqdm import tqdm
for i in tqdm(range(len(game_data))):
    try:
        keys = list(game_data[i].keys())
        gamedata = game_data[i]
        input_data = {'gameid': keys[1],
                      'win_team': gamedata[keys[1]],
                      '1' : gamedata[keys[2]][1],
                      '1score' : gamedata[keys[2]][0],
                      '2' : gamedata[keys[3]][1],
                      '2score' : gamedata[keys[3]][0],
                      '3' : gamedata[keys[4]][1],
                      '3score' : gamedata[keys[4]][0],
                      '4' : gamedata[keys[5]][1],
                      '4score' : gamedata[keys[5]][0],
                      '5' : gamedata[keys[6]][1],
                      '5score' : gamedata[keys[6]][0],
                      '6' : gamedata[keys[7]][1],
                      '6score' : gamedata[keys[7]][0],
                      '7' : gamedata[keys[8]][1],
                      '7score' : gamedata[keys[8]][0],
                      '8' : gamedata[keys[9]][1],
                      '8score' : gamedata[keys[9]][0],
                      '9' : gamedata[keys[10]][1],
                      '9score' : gamedata[keys[10]][0],
                      '10' : gamedata[keys[11]][1],
                      '10score' : gamedata[keys[11]][0],
                      }
        import sqlite3

        conn = sqlite3.connect('loldata.db') # 데이터 베이스 생성
        cur = conn.cursor()


        cur.execute(f"""INSERT OR REPLACE INTO Match_data("Id", "gameid", "win_team",  "1pick", "1score",
                                                                                        "2pick", "2score",
                                                                                        "3pick", "3score",
                                                                                        "4pick", "4score",
                                                                                        "5pick", "5score",
                                                                                        "6pick", "6score",
                                                                                        "7pick", "7score",
                                                                                        "8pick", "8score",
                                                                                        "9pick", "9score",
                                                                                        "10pick", "10score"
                                                                            )
                    VALUES ({i},?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);""", list(input_data.values()))

        conn.commit()
        cur.close
        conn.close

        learn_data = learn_data.append(input_data, ignore_index=True)
    except:
        pass

df = learn_data
df = df.drop_duplicates()
df = df.drop(['gameid'],axis =1) 
df = df.reset_index(drop = True)

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.model_selection import KFold
 
train, val =  train_test_split(df, test_size=0.2, train_size= 0.8, random_state=10)
target = 'win_team'
features = train.drop(columns=[target]).columns

X_train = train[features]
y_train = train[target]

X_val = val[features]
y_val = val[target]

from category_encoders import OrdinalEncoder
encoder = OrdinalEncoder()
X_train_encoded = encoder.fit_transform(X_train)
X_val_encoded = encoder.transform(X_val)

from xgboost import XGBClassifier
from sklearn.model_selection import GridSearchCV
xgb = XGBClassifier(n_jobs=-1,
                    random_state = 10)

dists = {'n_estimators' : [100,200,300,400,500,600],
        'learning_rate': [0.1, 0.2, 0.3],
        'max_depth' : [4,5,6,7]
        }

clf_xgb = GridSearchCV(
    xgb, 
    param_grid = dists,  
    cv=3, 
    scoring='f1',  
    verbose=1,
    )

print(clf_xgb.fit(X_train_encoded, y_train))