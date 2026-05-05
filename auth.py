from database import create_connection

def register_user(username,email,password):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO users(username,email,password) VALUES(?,?,?)",
        (username,email,password)
    )

    conn.commit()
    conn.close()

def login_user(email,password):

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE email=? AND password=?",
        (email,password)
    )

    user = cursor.fetchone()

    conn.close()
    return user
