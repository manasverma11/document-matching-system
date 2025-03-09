import sqlite3

conn = sqlite3.connect("database.db")
cur = conn.cursor()

cur.execute("""CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user',
    credits INTEGER DEFAULT 20
)""")

cur.execute("""CREATE TABLE documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    filename TEXT,
    path TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
)""")

cur.execute("""CREATE TABLE credit_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    credits INTEGER,
    status TEXT DEFAULT 'pending',
    FOREIGN KEY(user_id) REFERENCES users(id)
)""")

conn.commit()
conn.close()
