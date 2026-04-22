import sqlite3
import hashlib
from datetime import datetime, timedelta

DATABASE = 'leave_management.db'

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_tables():
    """Create required tables if they don't exist"""
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        leave_balance INTEGER
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS leaves (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER,
        leave_type TEXT,
        start_date TEXT,
        end_date TEXT,
        FOREIGN KEY(employee_id) REFERENCES employees(id)
    )
    ''')

    db.commit()
    db.close()

def setup_demo_data():
    """Create demo users and employees for testing"""
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    
    try:
        # Add demo users
        admin_password = hash_password('admin123')
        employee_password = hash_password('emp123')
        
        cursor.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                      ('admin', admin_password, 'admin'))
        cursor.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                      ('employee', employee_password, 'employee'))
        
        # Add demo employees
        cursor.execute('INSERT INTO employees (name, leave_balance) VALUES (?, ?)',
                      ('John Doe', 20))
        cursor.execute('INSERT INTO employees (name, leave_balance) VALUES (?, ?)',
                      ('Jane Smith', 20))
        cursor.execute('INSERT INTO employees (name, leave_balance) VALUES (?, ?)',
                      ('Mike Johnson', 20))
        
        # Add demo leave records
        today = datetime.now()
        tomorrow = today + timedelta(days=1)
        next_week = today + timedelta(days=7)
        
        cursor.execute('INSERT INTO leaves (employee_id, leave_type, start_date, end_date) VALUES (?, ?, ?, ?)',
                      (1, 'Annual', today.strftime('%Y-%m-%d'), tomorrow.strftime('%Y-%m-%d')))
        cursor.execute('INSERT INTO leaves (employee_id, leave_type, start_date, end_date) VALUES (?, ?, ?, ?)',
                      (2, 'Sick', next_week.strftime('%Y-%m-%d'), (next_week + timedelta(days=2)).strftime('%Y-%m-%d')))
        
        db.commit()
        print("✅ Demo data created successfully!")
        print("\nDemo Credentials:")
        print("Admin: username=admin, password=admin123")
        print("Employee: username=employee, password=emp123")
        
    except sqlite3.IntegrityError:
        print("⚠️ Demo data already exists or database issue.")
    finally:
        db.close()

if __name__ == '__main__':
    create_tables()        # ✅ THIS LINE FIXES YOUR ERROR
    setup_demo_data()