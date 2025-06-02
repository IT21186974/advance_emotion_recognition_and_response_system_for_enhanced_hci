import sqlite3

conn = sqlite3.connect('chat.db')
cursor = conn.cursor()

cursor.execute("SELECT * FROM users")
users = cursor.fetchall()
print("Users:")
for user in users:
    print(user)

cursor.execute("SELECT * FROM chat_messages")
messages = cursor.fetchall()
print("\nChat messages:")
for msg in messages:
    print(msg)

conn.close()
