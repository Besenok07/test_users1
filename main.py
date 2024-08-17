from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import sqlite3

app = FastAPI()

# Define the User model
class User(BaseModel):
    id: int
    username: str
    email: str

# Create a SQLite database and table if it does not exist
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        email TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

init_db()

# Retrieve all users
@app.get("/users", response_model=List[User])
async def get_users():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    conn.close()
    return [User(id=row[0], username=row[1], email=row[2]) for row in users]

# Retrieve a user by ID
@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return User(id=user[0], username=user[1], email=user[2])
    else:
        raise HTTPException(status_code=404, detail="User not found")

# Create a new user
@app.post("/create_user", response_model=User)
async def create_user(user: User):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (username, email) VALUES (?, ?)', (user.username, user.email))
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return User(id=user_id, username=user.username, email=user.email)
