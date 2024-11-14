from flask import g
import sqlite3
import os
from werkzeug.security import generate_password_hash

DATABASE = 'instance/hospital.db'

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    if not os.path.exists('instance'):
        os.makedirs('instance')
    
    print("Initializing database...")
    conn = sqlite3.connect(DATABASE)
    
    try:
        # Enable foreign keys
        conn.execute("PRAGMA foreign_keys = ON")
        
        # Read and execute schema
        with open('database/schema.sql', 'r') as f:
            schema_sql = f.read()
            print("Executing schema:")
            print(schema_sql)
            conn.executescript(schema_sql)
        
        conn.commit()
        
        # Verify tables were created
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print("Created tables:", [table[0] for table in tables])
        
    except sqlite3.Error as e:
        print(f"Database initialization error: {e}")
    finally:
        conn.close()

# Helper functions for user management
def get_user_by_email(email):
    db = get_db()
    return db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()

def get_user_by_id(user_id):
    db = get_db()
    return db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()

def create_user(user_data):
    db = get_db()
    try:
        db.execute('''
            INSERT INTO users (
                email, 
                password_hash, 
                name, 
                role, 
                confirmed
            ) VALUES (?, ?, ?, ?, ?)
        ''', (
            user_data['email'],
            user_data['password_hash'],
            user_data['name'],
            user_data['role'],
            1  # confirmed by default
        ))
        db.commit()
        return True
    except Exception as e:
        print(f"Error creating user: {e}")
        return False

def confirm_user_email(user_id):
    db = get_db()
    try:
        db.execute('UPDATE users SET confirmed = 1 WHERE id = ?', (user_id,))
        db.commit()
        return True
    except Exception as e:
        print(f"Error confirming user: {e}")
        return False

def get_user_by_confirmation_token(token):
    db = get_db()
    try:
        user = db.execute(
            'SELECT * FROM users WHERE confirmation_token = ?', 
            (token,)
        ).fetchone()
        return user
    except Exception as e:
        print(f"Error getting user by token: {e}")
        return None

def verify_db_structure():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("Current tables in database:", [table[0] for table in tables])
    return tables