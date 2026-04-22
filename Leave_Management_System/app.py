from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime, timedelta
import sqlite3
import hashlib
import os
from functools import wraps
import secrets
import string

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
                    role TEXT NOT NULL CHECK(role IN ('admin', 'employee')),
                    reset_token TEXT,
                    reset_token_expiry DATETIME
                );
                
                CREATE TABLE employees (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    name TEXT NOT NULL,
                    leave_balance INTEGER NOT NULL DEFAULT 20,
                    FOREIGN KEY (user_id) REFERENCES users(id)
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
            # Insert admin user only
            admin_pass = hash_password('admin123')
            db.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES ('admin', ?, 'admin')", (admin_pass,))
            db.commit()
            db.close()

# Hash password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Generate reset token
def generate_reset_token():
    return secrets.token_urlsafe(32)

# Validate reset token
def validate_reset_token(username, token):
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE username = ? AND reset_token = ?', (username, token)).fetchone()
    db.close()
    
    if not user:
        return None
    
    # Check if token has expired (24 hours)
    if user['reset_token_expiry']:
        expiry = datetime.strptime(user['reset_token_expiry'], '%Y-%m-%d %H:%M:%S')
        if datetime.now() > expiry:
            return None
    
    return user

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
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('employee_dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username = request.form['username']
        
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        
        if user:
            # Generate reset token
            token = generate_reset_token()
            expiry = datetime.now() + timedelta(hours=24)
            
            db.execute('UPDATE users SET reset_token = ?, reset_token_expiry = ? WHERE username = ?',
                      (token, expiry.strftime('%Y-%m-%d %H:%M:%S'), username))
            db.commit()
            
            # In a real app, send email with reset link
            # For now, display the reset link (for demo purposes)
            reset_url = url_for('reset_password', username=username, token=token, _external=True)
            flash(f'Password reset link: {reset_url}', 'info')
            flash('A password reset link has been generated. Use it within 24 hours.', 'success')
        else:
            flash('Username not found', 'danger')
        
        db.close()
        return redirect(url_for('login'))
    
    return render_template('forgot_password.html')

@app.route('/reset_password/<username>/<token>', methods=['GET', 'POST'])
def reset_password(username, token):
    user = validate_reset_token(username, token)
    
    if not user:
        flash('Invalid or expired reset token', 'danger')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        new_password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if new_password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('reset_password.html', username=username, token=token)
        
        if len(new_password) < 6:
            flash('Password must be at least 6 characters long', 'danger')
            return render_template('reset_password.html', username=username, token=token)
        
        db = get_db()
        hashed_pass = hash_password(new_password)
        db.execute('UPDATE users SET password = ?, reset_token = NULL, reset_token_expiry = NULL WHERE username = ?',
                  (hashed_pass, username))
        db.commit()
        db.close()
        
        flash('Password reset successful! You can now login with your new password.', 'success')
        return redirect(url_for('login'))
    
    return render_template('reset_password.html', username=username, token=token)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        leave_balance = int(request.form['leave_balance'])
        
        db = get_db()
        db.row_factory = sqlite3.Row
        
        # Check if username exists
        existing = db.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
        if existing:
            flash(f'Username "{username}" already exists. Choose another.', 'danger')
            db.close()
            return render_template('register.html')
        
        # Validate inputs
        if len(password) < 6:
            flash('Password must be at least 6 characters long', 'danger')
            db.close()
            return render_template('register.html')
        
        if leave_balance < 0:
            flash('Leave balance cannot be negative', 'danger')
            db.close()
            return render_template('register.html')
        
        try:
            # Insert user first
            hashed_pass = hash_password(password)
            cursor = db.execute('INSERT INTO users (username, password, role) VALUES (?, ?, "employee")', (username, hashed_pass))
            user_id = cursor.lastrowid
            
            # Insert employee linked to user
            db.execute('INSERT INTO employees (user_id, name, leave_balance) VALUES (?, ?, ?)', (user_id, name, leave_balance))
            db.commit()
            
            flash(f'Registration successful! Welcome {name}. You can now login with your username and password.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.rollback()
            flash('An error occurred during registration. Please try again.', 'danger')
            return render_template('register.html')
        finally:
            db.close()
    
    return render_template('register.html')

@app.route('/admin_dashboard')
@admin_required
def admin_dashboard():
    db = get_db()
    employees = db.execute('SELECT * FROM employees').fetchall()
    leaves = db.execute('SELECT l.*, e.name FROM leaves l JOIN employees e ON l.employee_id = e.id').fetchall()
    db.close()
    return render_template('admin_dashboard.html', employees=employees, leaves=leaves)

@app.route('/employee_dashboard')
@login_required
def employee_dashboard():
    db = get_db()
    
    # Get employee record for the logged-in user
    employee = db.execute('SELECT * FROM employees WHERE user_id = ?', (session['user_id'],)).fetchone()
    
    employee_id = employee['id'] if employee else None
    leaves = []
    remaining_balance = 0
    
    if employee_id:
        leaves = db.execute('SELECT * FROM leaves WHERE employee_id = ? ORDER BY start_date DESC', (employee_id,)).fetchall()
        remaining_balance = calculate_remaining_balance(db, employee_id)
    else:
        flash('No employee profile found. Please contact admin.', 'warning')
    
    db.close()
    return render_template('employee_dashboard.html', employee=employee, leaves=leaves, remaining_balance=remaining_balance)

@app.route('/dashboard')
@login_required
def dashboard():
    if session['role'] == 'admin':
        return redirect(url_for('admin_dashboard'))
    else:
        return redirect(url_for('employee_dashboard'))

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
        
        # Get employee record for logged-in user
        employee = db.execute('SELECT id FROM employees WHERE user_id = ?', (session['user_id'],)).fetchone()
        
        if not employee:
            flash('No employee record found for your account', 'danger')
            db.close()
            return redirect(url_for('dashboard'))
        
        try:
            # Validate dates
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            if end < start:
                flash('End date must be after start date', 'danger')
                return render_template('apply_leave.html')
        except ValueError:
            flash('Invalid date format', 'danger')
            return render_template('apply_leave.html')
        
        db.execute('INSERT INTO leaves (employee_id, leave_type, start_date, end_date) VALUES (?, ?, ?, ?)',
                  (employee['id'], leave_type, start_date, end_date))
        db.commit()
        db.close()
        
        flash('Leave application submitted successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    db.close()
    return render_template('apply_leave.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
