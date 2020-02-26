import sqlite3
import os
os.system('rm -rf database.db')

conn = sqlite3.connect('database.db')
print("Opened database successfully")

conn.execute('CREATE TABLE TASK (id INTEGER primary key AUTOINCREMENT, year TEXT, month TEXT, day TEXT, overview TEXT, detail TEXT, startTime TEXT, endTime TEXT)')
print("Table created successfully")

conn.commit()
conn.close()