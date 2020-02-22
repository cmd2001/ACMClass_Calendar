import sqlite3

conn = sqlite3.connect('database.db')
print("Database Connected")

print("Please input the id of task that you want to remove")
print("Warning: this operation CANNOT be revoked")
id = input()

cur = conn.cursor()

cur.execute("DELETE FROM TASK WHERE id = ?", id);
conn.commit()
conn.close()

print("Task successfully removed")
