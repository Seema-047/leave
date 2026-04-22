# Employee Registration - COMPLETE

**Full system now supports:**
- Navigation fixed (previous)
- Clean login (no demo)
- Role-based dashboards (/admin_dashboard, /employee_dashboard)
- **New: Self-registration for employees**
  - /register: Form (username, pass, name, balance) → users (role='employee') + employees
  - Duplicate username check
  - Link "Register here" on login.html

## Test:
1. `cd "d:/employee/Leave_Management_System" && python app.py`
2. New employee: http://127.0.0.1:5000/register → Register → Login with new creds
3. Existing: admin/admin123, employee/emp123

Admin can still add employees. Production: Link user/employee IDs.

Task complete.

