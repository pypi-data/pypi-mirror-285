# usl/utils/db.py

import sqlite3
import os
import json

# Constants
DB_FILE = os.path.join(os.path.expanduser("~"), ".tunnelspider", "config.db")

# Ensure the directory exists
os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)

# Initialize database
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS config (
                 key TEXT PRIMARY KEY,
                 value TEXT NOT NULL)''')
    conn.commit()
    conn.close()

# Set a configuration value
def set_config(key, value):
    init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('REPLACE INTO config (key, value) VALUES (?, ?)', (key, value))
    conn.commit()
    conn.close()

# Get a configuration value
def get_config(key=None):
    init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    if key:
        c.execute('SELECT value FROM config WHERE key=?', (key,))
        result = c.fetchone()
        conn.close()
        return result[0] if result else None
    else:
        c.execute('SELECT key, value FROM config')
        rows = c.fetchall()
        conn.close()
        return json.dumps({key: value for key, value in rows}, indent=4)
