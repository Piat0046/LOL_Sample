conn = sqlite3.connect('loldata.db')
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS champID;")

cur.execute(f"""CREATE TABLE ChampID (
				ID INTEGER NOT NULL PRIMARY KEY,
                Name NVARCHAR(160);
			""")

for val in list_data[1:11]:
    cur.execute(f"INSERT INTO Albums_Part1({list_data[0][0]},{list_data[0][1]},{list_data[0][2]}) VALUES (?,?,?);", val)

conn.commit()
cur.close
conn.close