import sqlite3

conn = sqlite3.connect('database.db')
print("Database Connected")

print("Please input Year number")
year = str(input())
print("Please input Month number")
month = str(input())
print("Please input Day number")
day = str(input())
print("Please input Task Overview")
overview = str(input())
print("Please input Task Detail")
detial = str(input())

cur = conn.cursor()

cur.execute("INSERT INTO TASK (id, year, month, day, overview, detail) VALUES (NULL, ?, ?, ?, ?, ?)", (year, month, day, overview, detial));
conn.commit()
conn.close()

print("Data Inserted")
