import sqlite3

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            patient_name TEXT NOT NULL,
            patient_gender TEXT,
            patient_age INTEGER,
            diagnosis_type TEXT,
            diagnosis_result TEXT,
            diagnosis_date TEXT NOT NULL,
            notes TEXT
        )
    ''')
    conn.commit()
    conn.close()

def create_user(username, password):
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def check_user(username, password):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
    conn.close()
    return user is not None

def add_record(username, patient_name, patient_gender, patient_age, diagnosis_type, diagnosis_result, diagnosis_date, notes):
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO records (
            username, patient_name, patient_gender, patient_age,
            diagnosis_type, diagnosis_result, diagnosis_date, notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (username, patient_name, patient_gender, patient_age,
          diagnosis_type, diagnosis_result, diagnosis_date, notes))
    conn.commit()
    conn.close()

def get_user_records(username):
    conn = get_db_connection()
    records = conn.execute('SELECT * FROM records WHERE username = ? ORDER BY diagnosis_date DESC', (username,)).fetchall()
    conn.close()
    return records

def search_records(username, search_name):
    conn = get_db_connection()
    records = conn.execute('SELECT * FROM records WHERE username = ? AND patient_name LIKE ?', (username, f'%{search_name}%')).fetchall()
    conn.close()
    return records
