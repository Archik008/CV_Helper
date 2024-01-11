import sqlite3

db = sqlite3.connect('data/user_database.db')
cursor = db.cursor()

def create_tables():
    cursor.execute("CREATE TABLE IF NOT EXISTS users(userid INTEGER PRIMARY KEY, personal_data TEXT, purpose TEXT, exp TEXT, education TEXT, personal_qualities TEXT)")
    db.commit()

def add_user(user_id: int, personal_data, purpose, exp, education, personal_qualities):
    cursor.execute("INSERT INTO users VALUES(?, ?, ?, ?, ?, ?)", (user_id, personal_data, purpose, exp, education, personal_qualities))
    db.commit()

def get_user(user_id: int):
    cursor.execute("SELECT * FROM users WHERE userid = ?", (user_id, ))

    cursor_result = cursor.fetchone()
    if cursor_result is None:
        return None
    return cursor_result

def update_user_column(user_id: int, keys_to_update: dict):
    for key in keys_to_update:
        value = keys_to_update[key]
        
        cursor.execute(f"UPDATE users SET {key} = '{value}' WHERE userid = {user_id}")
        db.commit()

create_tables()