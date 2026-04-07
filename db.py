import sqlite3
import pandas as pd
from datetime import datetime
import os

DB_PATH = "data/sahaya.db"

def get_db_connection():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    full_name TEXT NOT NULL,
                    role TEXT NOT NULL CHECK(role IN ('admin', 'donor', 'receiver')),
                    is_active BOOLEAN DEFAULT 1,
                    phone TEXT,
                    email TEXT,
                    address TEXT
                )''')
    
    # Safe migration for columns
    try:
        c.execute("ALTER TABLE users ADD COLUMN phone TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        c.execute("ALTER TABLE users ADD COLUMN email TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        c.execute("ALTER TABLE users ADD COLUMN address TEXT")
    except sqlite3.OperationalError:
        pass

    c.execute('''CREATE TABLE IF NOT EXISTS donations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    donor_username TEXT,
                    category TEXT,
                    title TEXT,
                    description TEXT,
                    quantity INTEGER,
                    token_amount INTEGER DEFAULT 0,
                    donor_note TEXT,
                    image_path TEXT,
                    status TEXT DEFAULT 'available',
                    created_at TEXT
                )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    receiver_username TEXT,
                    donation_id INTEGER,
                    category TEXT,
                    title TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at TEXT
                )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    donation_id INTEGER,
                    receiver_username TEXT,
                    amount INTEGER,
                    payment_status TEXT DEFAULT 'paid',
                    paid_at TEXT
                )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    receiver_username TEXT,
                    donation_id INTEGER,
                    title TEXT,
                    rating INTEGER,
                    feedback_text TEXT,
                    proof_image_path TEXT,
                    created_at TEXT
                )''')

    conn.commit()
    conn.close()

def create_default_data():
    conn = get_db_connection()
    c = conn.cursor()
    default_users = [
        ("admin", "admin123", "Super Admin", "admin", "", ""),
        ("donor1", "123", "Rahul Sharma", "donor", "", ""),
        ("receiver1", "123", "Priya Patel", "receiver", "", "")
    ]
    for user in default_users:
        c.execute("SELECT * FROM users WHERE username = ?", (user[0],))
        if not c.fetchone():
            c.execute("""INSERT INTO users 
                        (username, password, full_name, role, is_active, phone, email) 
                        VALUES (?, ?, ?, ?, 1, ?, ?)""", user)
    conn.commit()
    conn.close()

def add_user(username, password, full_name, role, phone="", email=""):
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute("""INSERT INTO users 
                    (username, password, full_name, role, is_active, phone, email) 
                    VALUES (?, ?, ?, ?, 1, ?, ?)""",
                  (username, password, full_name, role, phone, email))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def get_user(username, password):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""SELECT * FROM users 
                 WHERE username=? AND password=? AND is_active=1""", 
              (username, password))
    user = c.fetchone()
    conn.close()
    return dict(user) if user else None

def update_profile(username, full_name, phone, email, address=""):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""UPDATE users 
                 SET full_name = ?, 
                     phone = ?, 
                     email = ?, 
                     address = ? 
                 WHERE username = ?""",
              (full_name, phone, email, address, username))
    conn.commit()
    conn.close()
    return True

# ====================== DONATION FUNCTIONS ======================
def add_donation(donor_username, category, title, description, quantity, token_amount=0, donor_note="", image_path=""):
    conn = get_db_connection()
    c = conn.cursor()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    c.execute("""INSERT INTO donations 
                 (donor_username, category, title, description, quantity, token_amount, donor_note, image_path, created_at) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
              (donor_username, category, title, description, quantity, token_amount, donor_note, image_path, created_at))
    conn.commit()
    conn.close()

def get_donations():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM donations ORDER BY created_at DESC", conn)
    conn.close()
    return df

# ====================== REQUEST & PAYMENT FUNCTIONS ======================
def get_requests():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM requests ORDER BY created_at DESC", conn)
    conn.close()
    return df

def get_payments():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM payments ORDER BY paid_at DESC", conn)
    conn.close()
    return df

def add_request(receiver_username, donation_id, category, title):
    conn = get_db_connection()
    c = conn.cursor()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    c.execute("""INSERT INTO requests 
                 (receiver_username, donation_id, category, title, status, created_at) 
                 VALUES (?, ?, ?, ?, 'pending', ?)""",
              (receiver_username, donation_id, category, title, created_at))
    conn.commit()
    conn.close()

def update_request_status(request_id, status):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("UPDATE requests SET status=? WHERE id=?", (status, request_id))
    conn.commit()
    conn.close()

def record_payment(donation_id, receiver_username, amount):
    conn = get_db_connection()
    c = conn.cursor()
    paid_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    c.execute("""INSERT INTO payments 
                 (donation_id, receiver_username, amount, payment_status, paid_at) 
                 VALUES (?, ?, ?, 'paid', ?)""", 
              (donation_id, receiver_username, amount, paid_at))
    conn.commit()
    conn.close()

# ====================== ADMIN FUNCTIONS ======================
def get_users():
    conn = get_db_connection()
    df = pd.read_sql_query("""
        SELECT id, username, full_name, role, COALESCE(is_active, 1) as is_active, 
               phone, email, address 
        FROM users ORDER BY id DESC
    """, conn)
    conn.close()
    return df

def update_user_role(user_id, new_role):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET role = ? WHERE id = ?", (new_role, user_id))
    conn.commit()
    conn.close()

def deactivate_user(user_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET is_active = 0 WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

def delete_donation(donation_id):
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute("DELETE FROM donations WHERE id = ?", (donation_id,))
        c.execute("DELETE FROM requests WHERE donation_id = ?", (donation_id,))
        c.execute("DELETE FROM payments WHERE donation_id = ?", (donation_id,))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

# ====================== FEEDBACK FUNCTIONS ======================
def add_feedback(receiver_username, donation_id, title, rating, feedback_text, proof_image_path=""):
    conn = get_db_connection()
    c = conn.cursor()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    c.execute("""INSERT INTO feedback 
                 (receiver_username, donation_id, title, rating, feedback_text, proof_image_path, created_at) 
                 VALUES (?, ?, ?, ?, ?, ?, ?)""",
              (receiver_username, donation_id, title, rating, feedback_text, proof_image_path, created_at))
    conn.commit()
    conn.close()

def get_feedback():
    conn = get_db_connection()
    df = pd.read_sql_query("""
        SELECT f.*, d.donor_username 
        FROM feedback f
        LEFT JOIN donations d ON f.donation_id = d.id
        ORDER BY f.created_at DESC
    """, conn)
    conn.close()
    return df