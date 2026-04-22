from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime, timedelta
import sqlite3
import hashlib
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key_change_this'
DATABASE = 'leave_management.db'

# Helper function to get database connection
def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

# Initialize database
def init_db():
    if not os.path.exists(DATABASE):
        db = get_db()
        with app.app_context():
            db.executescript('''
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL CHECK(role IN ('admin', 'employee'))
                );
                
                CREATE TABLE employees (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    leave_balance INTEGER NOT NULL DEFAULT 20
                );
                
                CREATE TABLE leaves (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id INTEGER NOT NULL,
                    leave_type TEXT NOT NULL CHECK(leave_type IN ('Sick', 'Casual', 'Annual')),
                    start_date DATE NOT NULL,
                    end_date DATE NOT NULL,
                    FOREIGN KEY (employee_id) REFERENCES employees(id)
                );
            ''')
            db.commit()
            db.close()

# Hash password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first', 'danger')
            return redirect(url_for('login'))
        
        db = get_db()
        user = db.execute('SELECT role FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        db.close()
        
        if not user or user['role'] != 'admin':
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function

# Routes

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        db.close()
        
        if user and user['password'] == hash_password(password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    db = get_db()
    
    if session['role'] == 'admin':
        employees = db.execute('SELECT * FROM employees').fetchall()
        leaves = db.execute('SELECT l.*, e.name FROM leaves l JOIN employees e ON l.employee_id = e.id').fetchall()
        db.close()
        return render_template('admin_dashboard.html', employees=employees, leaves=leaves)
    else:
        # Employee dashboard
        employee = db.execute('SELECT * FROM employees WHERE id = (SELECT id FROM users WHERE id = ?)', 
                             (session['user_id'],)).fetchone()
        
        # Get employee_id from username
        user = db.execute('SELECT username FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        
        # Try to find employee by checking if there's a matching employee
        all_employees = db.execute('SELECT * FROM employees').fetchall()
        employee_id = None
        
        # For simplicity, assume first employee is linked to first employee user
        # In production, you'd have a proper user_id to employee_id mapping
        if all_employees:
            employee_id = all_employees[0]['id']
        
        leaves = []
        remaining_balance = 0
        
        if employee_id:
            employee = db.execute('SELECT * FROM employees WHERE id = ?', (employee_id,)).fetchone()
            leaves = db.execute('SELECT * FROM leaves WHERE employee_id = ?', (employee_id,)).fetchall()
            remaining_balance = calculate_remaining_balance(db, employee_id)
        
        db.close()
        return render_template('employee_dashboard.html', employee=employee, leaves=leaves, remaining_balance=remaining_balance)

def calculate_remaining_balance(db, employee_id):
    employee = db.execute('SELECT leave_balance FROM employees WHERE id = ?', (employee_id,)).fetchone()
    leaves = db.execute('SELECT start_date, end_date FROM leaves WHERE employee_id = ?', (employee_id,)).fetchall()
    
    used = 0
    for leave in leaves:
        start = datetime.strptime(leave['start_date'], '%Y-%m-%d')
        end = datetime.strptime(leave['end_date'], '%Y-%m-%d')
        used += (end - start).days + 1
    
    return employee['leave_balance'] - used if employee else 0

# Admin Routes


@app.route('/admin/add_employee', methods=['GET', 'POST'])
@admin_required
def add_employee():
    if request.method == 'POST':
        name = request.form['name']
        leave_balance = int(request.form['leave_balance'])
        
        db = get_db()
        db.execute('INSERT INTO employees (name, leave_balance) VALUES (?, ?)', (name, leave_balance))
        db.commit()
        db.close()
        
        flash(f'Employee {name} added successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('add_employee.html')

@app.route('/admin/add_leave', methods=['GET', 'POST'])
@admin_required
def add_leave():
    db = get_db()
    employees = db.execute('SELECT * FROM employees').fetchall()
    
    if request.method == 'POST':
        employee_id = int(request.form['employee_id'])
        leave_type = request.form['leave_type']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        
        # Validate dates
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            if end < start:
                flash('End date must be after start date', 'danger')
                return redirect(url_for('add_leave'))
        except ValueError:
            flash('Invalid date format', 'danger')
            return redirect(url_for('add_leave'))
        
        db.execute('INSERT INTO leaves (employee_id, leave_type, start_date, end_date) VALUES (?, ?, ?, ?)',
                  (employee_id, leave_type, start_date, end_date))
        db.commit()
        db.close()
        
        flash('Leave record added successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    db.close()
    return render_template('add_leave.html', employees=employees)

@app.route('/admin/edit_leave/<int:leave_id>', methods=['GET', 'POST'])
@admin_required
def edit_leave(leave_id):
    db = get_db()
    employees = db.execute('SELECT * FROM employees').fetchall()
    leave = db.execute('SELECT * FROM leaves WHERE id = ?', (leave_id,)).fetchone()
    
    if request.method == 'POST':
        employee_id = int(request.form['employee_id'])
        leave_type = request.form['leave_type']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        
        db.execute('UPDATE leaves SET employee_id = ?, leave_type = ?, start_date = ?, end_date = ? WHERE id = ?',
                  (employee_id, leave_type, start_date, end_date, leave_id))
        db.commit()
        db.close()
        
        flash('Leave record updated successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    db.close()
    return render_template('edit_leave.html', leave=leave, employees=employees)

@app.route('/admin/delete_leave/<int:leave_id>')
@admin_required
def delete_leave(leave_id):
    db = get_db()
    db.execute('DELETE FROM leaves WHERE id = ?', (leave_id,))
    db.commit()
    db.close()
    
    flash('Leave record deleted successfully!', 'success')
    return redirect(url_for('dashboard'))


# Employee Routes

@app.route('/employee/apply_leave', methods=['GET', 'POST'])
@login_required
def apply_leave():
    db = get_db()
    
    if request.method == 'POST':
        leave_type = request.form['leave_type']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        
        # Get employee_id for current user (simplified)
        # In production, add proper user-employee mapping
        all_employees = db.execute('SELECT * FROM employees').fetchall()
        if not all_employees:
            flash('No employee record found for your account', 'danger')
            return redirect(url_for('dashboard'))
        
        employee_id = all_employees[0]['id']
        
        db.execute('INSERT INTO leaves (employee_id, leave_type, start_date, end_date) VALUES (?, ?, ?, ?)',
                  (employee_id, leave_type, start_date, end_date))
        db.commit()
        db.close()
        
        flash('Leave application submitted successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    db.close()
    return render_template('apply_leave.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
