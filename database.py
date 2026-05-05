import sqlite3

def create_connection():
    conn = sqlite3.connect("database.db")
    return conn

def create_tables():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        email TEXT,
        password TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS analysis(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        file_name TEXT,
        total_messages INTEGER,
        total_words INTEGER,
        media_messages INTEGER,
        links_shared INTEGER
    )
    """)

    conn.commit()
    conn.close()
