from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime

DB_PATH = "database.db"

class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()
    print("Database initialized - users table ready")


def register_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    password_hash = generate_password_hash(password)
    try:
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
        conn.commit()
        print(f"User '{username}' registered successfully")
        return True
    except sqlite3.IntegrityError:
        print(f"Username '{username}' already exists")
        return False
    finally:
        conn.close()


def verify_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password_hash FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    if row and check_password_hash(row[2], password):
        print(f"Login successful for '{username}'")
        return User(row[0], row[1], row[2])
    else:
        print("Invalid username or password")
        return None


def init_watermarks_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS watermarks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            image_name TEXT NOT NULL,
            watermark_text TEXT NOT NULL,
            wm_bits INTEGER NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()
    print("Watermarks table initialized")


def save_watermark(username, image_name, watermark_text, wm_bits):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO watermarks (username, image_name, watermark_text, wm_bits, timestamp) VALUES (?, ?, ?, ?, ?)",
        (username, image_name, watermark_text, wm_bits, timestamp)
    )
    conn.commit()
    conn.close()


def get_watermark(image_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT watermark_text, wm_bits FROM watermarks WHERE image_name = ?", (image_name,))
    row = cursor.fetchone()
    conn.close()
    return row


if __name__ == "__main__":
    init_db()
    init_watermarks_table()
    register_user("sree", "testpass123")
    verify_user("sree", "testpass123")
