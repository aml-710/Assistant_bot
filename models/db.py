# db.py
import sqlite3

def connect():
    return sqlite3.connect("data/bot.db")

def create_tables():
    conn = connect()
    cursor = conn.cursor()

    # таблица расписания
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS schedule (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        day TEXT,
        text TEXT
    )
    """)

    # таблица заметок
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        text TEXT
    )
    """)

    # таблица напоминаний
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reminders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        text TEXT,
        due_ts INTEGER
    )
    """)

    conn.commit()
    conn.close()