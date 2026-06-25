import sqlite3
from datetime import datetime

DB_PATH = "database.db"

def init_audit_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            action TEXT NOT NULL,
            details TEXT,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()
    print("Audit table initialized")

def log_action(username, action, details=""):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO audit_log (username, action, details, timestamp) VALUES (?, ?, ?, ?)",
        (username, action, details, timestamp)
    )
    conn.commit()
    conn.close()
    print(f"[AUDIT] {timestamp} | {username} | {action} | {details}")

def get_audit_log(username=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if username:
        cursor.execute("SELECT * FROM audit_log WHERE username = ?", (username,))
    else:
        cursor.execute("SELECT * FROM audit_log")
    rows = cursor.fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    init_audit_table()
    log_action("sree", "REGISTER", "New user account created")
    log_action("sree", "LOGIN", "Successful login")
    log_action("sree", "WATERMARK_EMBED", "test_image.jpg watermarked")
    
    print("\nFull audit log:")
    for row in get_audit_log():
        print(row)