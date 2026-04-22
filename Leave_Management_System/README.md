# 📋 Leave Management System

A web-based Leave Management System that helps manage employee leave requests. The system includes a login feature and role-based access for admins and employees.

## 🌟 Features

### 🔐 Authentication
- User login with username and password
- Role-based access control (Admin / Employee)
- Session management

### 👑 Admin Features
- ➕ Add new employees
- 🏢 Set and manage leave balance
- 📊 View all leave records
- ✏️ Add, edit, and delete leave entries
- 📅 Track all employee leaves

### 👤 Employee Features
- 📝 Apply for leave
- 📅 View leave history
- 💰 Check remaining leave balance
- 📊 View total leave balance

## 🗄️ Database Schema

### Users Table
```
id          - User ID
username    - Unique username
password    - Hashed password
role        - 'admin' or 'employee'
```

### Employees Table
```
id              - Employee ID
name            - Employee name
leave_balance   - Total leave balance
```

### Leaves Table
```
id              - Leave record ID
employee_id     - Reference to employee
leave_type      - Type of leave (Sick/Casual/Annual)
start_date      - Leave start date
end_date        - Leave end date
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Step 1: Install Dependencies
```bash
cd d:\employee\Leave_Management_System
pip install -r requirements.txt
```

### Step 2: Run the Setup Script (Optional)
This creates demo data for testing:
```bash
python setup.py
```

### Step 3: Run the Application
```bash
python app.py
```

The application will start on `http://localhost:5000`

## 📝 Demo Credentials

If you ran the setup script, use these credentials:

**Admin Account:**
- Username: `admin`
- Password: `admin123`

**Employee Account:**
- Username: `employee`
- Password: `emp123`

## 🎯 User Guide

### For Admins
1. **Login** with admin credentials
2. **Add Employees** - Click "➕ Add Employee" to create new employee records
3. **Manage Leaves** - Add, edit, or delete leave records for employees
4. **View Reports** - Check all employee leave records in one place

### For Employees
1. **Login** with your credentials
2. **View Dashboard** - See your leave balance and history
3. **Apply for Leave** - Click "📝 Apply for Leave" to submit a leave request
4. **Check History** - View all your previous leave applications

## 📁 Project Structure
```
Leave_Management_System/
├── app.py                      # Main Flask application
├── setup.py                    # Setup script for demo data
├── requirements.txt            # Python dependencies
├── leave_management.db         # SQLite database (created on first run)
├── templates/                  # HTML templates
│   ├── base.html              # Base template
│   ├── login.html             # Login page
│   ├── admin_dashboard.html   # Admin dashboard
│   ├── employee_dashboard.html # Employee dashboard
│   ├── add_employee.html      # Add employee form
│   ├── add_leave.html         # Add leave record form
│   ├── edit_leave.html        # Edit leave record form
│   └── apply_leave.html       # Apply for leave form
└── static/                     # Static files
    └── style.css              # Stylesheet
```

## 🔒 Security Notes

⚠️ **Important**: This is a demo application. For production use:
1. Change the secret key in `app.py`
2. Use proper password hashing (bcrypt, argon2)
3. Add CSRF protection
4. Use HTTPS
5. Implement proper authentication (JWT, OAuth)
6. Add input validation and sanitization
7. Use a production database (PostgreSQL, MySQL)
8. Add logging and error handling
9. Implement proper access controls
10. Add audit trails

## 🎨 Tech Stack
- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **Database**: SQLite
- **Styling**: Custom CSS with responsive design

## 📱 Responsive Design
The application is fully responsive and works on:
- Desktop computers
- Tablets
- Mobile devices

## 🐛 Troubleshooting

### Port Already in Use
If port 5000 is already in use, modify the last line in `app.py`:
```python
app.run(debug=True, port=5001)
```

### Database Issues
If you encounter database errors, delete `leave_management.db` and restart the app.

### Login Issues
- Ensure you've run `setup.py` to create demo accounts
- Double-check username and password
- Clear browser cookies and try again

## 📞 Support
For issues or questions, review the code comments in `app.py` for detailed explanations.

## 📄 License
This project is open source and available for educational purposes.

---

**Created**: April 2026
**Version**: 1.0
