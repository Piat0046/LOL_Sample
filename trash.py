import sqlite3

conn = sqlite3.connect('loldata.db')
cur = conn.cursor()
gameId_list = [] 
for row in cur.execute("SELECT ci.Name FROM ChampID ci ORDER BY Name ASC"):
    gameId_list.append(str(row).split('\'')[1])

conn.commit()
cur.close
conn.close

print(gameId_list)