# AcuMeds Installation & Deployment Guide

## System Requirements

- Python 3.8 or higher
- pip (Python package manager)
- At least 100MB disk space
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Windows, Mac, or Linux OS

## Step-by-Step Installation

### Phase 1: Environment Setup (5-10 minutes)

#### Step 1.1: Navigate to Project Directory
```bash
cd "d:\CODING\Aryan darling\pharmacy_system"
```

#### Step 1.2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Expected Output:**
```
(venv) C:\...\pharmacy_system>
```

#### Step 1.3: Upgrade pip
```bash
python -m pip install --upgrade pip
```

### Phase 2: Install Dependencies (3-5 minutes)

```bash
pip install -r requirements.txt
```

**Files to be installed:**
- Flask 2.3.0
- Flask-SQLAlchemy 3.0.3
- Flask-Login 0.6.2
- Werkzeug 2.3.0

**Verify Installation:**
```bash
pip list
```

Should see:
- Flask (2.3.0 or higher)
- Flask-SQLAlchemy (3.0.3 or higher)
- Flask-Login (0.6.2 or higher)

### Phase 3: Database Setup (2-3 minutes)

#### Step 3.1: Initialize Database
```bash
python database/db_init.py
```

**Expected Output:**
```
Database initialized successfully at /path/to/pharmacy.db
Sample data added successfully!
```

**What gets created:**
- `database/pharmacy.db` (SQLite database file)
- 7 database tables
- 15 sample medicines
- 1 admin user (admin@pharmacy.com / admin123)

#### Step 3.2: Verify Database Creation
```bash
# Check if file exists (Windows)
dir database\pharmacy.db

# Check if file exists (Mac/Linux)
ls -la database/pharmacy.db
```

File should be present in the `database/` folder.

### Phase 4: Configuration (1-2 minutes)

#### Step 4.1: Review Configuration
```bash
# Edit app/__init__.py if needed
# Check SECRET_KEY matches your environment
```

**For Development (default):**
- DEBUG = True (auto-reload enabled)
- Running on localhost:5000
- SQLite database in project directory

**For Production:**
- Change SECRET_KEY in app/__init__.py
- Set DEBUG = False
- Use external database (MySQL/PostgreSQL)
- Enable HTTPS

#### Step 4.2: Configure Upload Directory
The `static/uploads/` folder is ready to receive files.

### Phase 5: Launch Application (1 minute)

#### Step 5.1: Start Flask Server
```bash
python run.py
```

**Expected Output:**
```
 * Running on http://127.0.0.1:5000 (Press CTRL+C to quit)
 * Restarting with reloader
 * Debugger is active!
```

#### Step 5.2: Verify Server is Running
- Server should start without errors
- Shows "Running on localhost:5000" or similar
- No "Address already in use" errors

### Phase 6: Access Application (1 minute)

#### Step 6.1: Open Web Browser
```
http://localhost:5000/
```

**Should See:**
- AcuMeds homepage
- Navigation bar with links
- Featured medicines section

#### Step 6.2: Test Login
1. Click "Login" in navbar
2. Enter credentials:
   - Email: `admin@pharmacy.com`
   - Password: `admin123`
3. Click "Login"
4. Should see admin dashboard

---

## Verification Checklist

After installation, verify everything works:

- [ ] Python installed and virtual environment activated
- [ ] All dependencies installed (`pip list` shows Flask, etc.)
- [ ] Database file created at `database/pharmacy.db`
- [ ] Server starts without errors (`python run.py`)
- [ ] Can access `http://localhost:5000` in browser
- [ ] Homepage loads with medicines
- [ ] Can login with admin@pharmacy.com / admin123
- [ ] Admin dashboard loads
- [ ] Can browse medicines
- [ ] Can use AI recommendations
- [ ] Shopping cart functionality works

---

## Common Issues & Solutions

### Issue 1: Python Command Not Found
**Error:** `'python' is not recognized as an internal or external command`

**Solution:**
- Check Python installation: `python --version`
- On some systems use `python3` instead
- Add Python to PATH environment variable

### Issue 2: pip Install Fails
**Error:** `ERROR: Could not find a version that satisfies the requirement`

**Solution:**
```bash
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir
```

### Issue 3: Virtual Environment Not Activating
**Error:** After running activate, nothing seems to happen

**Solution (Windows):**
```bash
# Try with full path
venv\Scripts\activate.bat
# Or use Python to run it
python -m venv venv
venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Issue 4: Database Not Found
**Error:** `FileNotFoundError: database/pharmacy.db not found`

**Solution:**
```bash
python database/db_init.py
# Wait for "Database initialized successfully" message
```

### Issue 5: Port 5000 Already in Use
**Error:** `Address already in use` or `Port 5000 in use`

**Solution (Windows):**
```bash
# Find process using port 5000
netstat -ano | findstr :5000
# Kill process (replace PID with actual number)
taskkill /PID <PID> /F

# Or change port in run.py
app.run(debug=True, host='0.0.0.0', port=5001)
```

**Solution (Mac/Linux):**
```bash
# Find process
lsof -i :5000
# Kill process
kill -9 <PID>
```

### Issue 6: Import Errors When Running Server
**Error:** `ModuleNotFoundError: No module named 'flask'`

**Solution:**
1. Confirm virtual environment is activated (should see `(venv)` in prompt)
2. Reinstall dependencies: `pip install -r requirements.txt`
3. Verify: `python -c "import flask; print(flask.__version__)"`

### Issue 7: Login Fails Even with Correct Credentials
**Error:** "Invalid email or password"

**Solution:**
1. Make sure database was initialized: `python database/db_init.py`
2. Check database file exists: `ls database/pharmacy.db`
3. Start server fresh: stop and `python run.py` again

### Issue 8: Static Files (CSS/JavaScript) Not Loading
**Issue:** Website appears unstyled

**Solution:**
1. Check folder structure exists:
   ```
   static/
   ├── css/style.css
   ├── js/main.js
   └── uploads/
   ```
2. Restart server: Press Ctrl+C and `python run.py`
3. Hard refresh browser: Ctrl+Shift+R (or Cmd+Shift+R on Mac)

---

## Deployment Guides

### Option 1: Deploy on PythonAnywhere

1. Create account at pythonywhere.com
2. Upload project files
3. Set up virtual environment
4. Configure WSGI file
5. Reload web app
6. Access at yourusername.pythonanywhere.com

### Option 2: Deploy on Heroku

1. Install Heroku CLI
2. Create `Procfile`:
   ```
   web: gunicorn run:app
   ```
3. Add to requirements.txt:
   ```
   gunicorn==21.2.0
   ```
4. Deploy:
   ```bash
   heroku login
   heroku create app-name
   git push heroku main
   ```

### Option 3: Deploy on DigitalOcean

1. Create Ubuntu droplet
2. Install Python and PostgreSQL
3. Clone project
4. Set up virtual environment
5. Install Nginx and Gunicorn
6. Configure Nginx reverse proxy
7. Get SSL with LetsEncrypt
8. Start application

### Option 4: Deploy with Docker

1. Create Dockerfile:
   ```dockerfile
   FROM python:3.9
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   CMD ["python", "run.py"]
   ```

2. Build and run:
   ```bash
   docker build -t pharmacy .
   docker run -p 5000:5000 pharmacy
   ```

---

## Post-Installation Configuration

### Change Admin Password
```bash
python
>>> from app import db, create_app
>>> from app.models import User
>>> app = create_app()
>>> with app.app_context():
>>>     admin = User.query.filter_by(email='admin@pharmacy.com').first()
>>>     admin.set_password('new-password')
>>>     db.session.commit()
>>>     print("Password changed!")
```

### Add New Medicines
1. Login as admin
2. Go to Admin Panel
3. Click "Add New Medicine"
4. Fill in details
5. Click Submit

### Configure Database for Production

**Switch to MySQL:**
```python
# In app/__init__.py
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://user:password@localhost/pharmacy'
```

Then install:
```bash
pip install pymysql
```

---

## Maintenance & Operations

### Regular Tasks

**Daily:**
- Monitor server logs
- Check for errors
- Verify application responsiveness

**Weekly:**
- Review orders
- Update inventory
- Check system performance

**Monthly:**
- Database backup
- Security audit
- Performance analysis

### Database Backup

```bash
# SQLite backup
cp database/pharmacy.db database/pharmacy.db.backup

# Schedule automated backups (cron on Linux)
0 2 * * * cp /path/pharmacy.db /backups/pharmacy_$(date +\%Y\%m\%d).db
```

### View Application Logs
```bash
# If using file logging
tail -f logs/app.log

# For server output
# Check the terminal where `python run.py` is running
```

---

## Performance Optimization

### Caching
- Browser caches CSS/JS files
- Database indexes already set up
- Session caching available

### Database Optimization
- Indexes on user_id, medicine_id, category
- Efficient ORM queries
- Connection pooling ready

### Static Files
- Compress images before upload
- Minify CSS/JS for production
- Use CDN for Bootstrap/FontAwesome

---

## Security Checklist

Before Going Live:

- [ ] Change SECRET_KEY from default
- [ ] Set DEBUG = False in production
- [ ] Use strong admin password
- [ ] Set up HTTPS/SSL certificate
- [ ] Configure CSRF protection
- [ ] Enable input validation
- [ ] Set up database backups
- [ ] Review user permissions
- [ ] Configure firewall rules
- [ ] Monitor for suspicious activity

---

## Troubleshooting Quick Links

- **Won't Start?** → Check Issue 4, 5, 6
- **Database Error?** → Check Issue 7, 8
- **Login Issues?** → Check Issue 7
- **Styling Issues?** → Check Issue 8
- **Crashes?** → Check Python version (3.8+)

---

## Getting Help

**If stuck:**
1. Check README.md for full documentation
2. Review QUICKSTART.md for quick reference
3. Check inline code comments
4. Review error messages carefully
5. Ensure all prerequisites met

---

## Success Criteria

Installation is successful when you can:

✅ Access http://localhost:5000  
✅ Login with admin credentials  
✅ Browse medicines  
✅ Use search functionality  
✅ Add items to cart  
✅ Place an order  
✅ Use AI recommendations  
✅ Access admin panel  
✅ Add/edit medicines as admin  
✅ Update order status  

---

## Next Steps After Installation

1. **Explore the application**
   - Register as new user
   - Browse medicines
   - Test shopping cart
   - Try AI recommendations

2. **Customize for your needs**
   - Modify sample medicines
   - Add more categories
   - Update branding
   - Change colors/styling

3. **Prepare for deployment**
   - Set up domain name
   - Configure SSL certificate
   - Set up email service
   - Configure analytics

4. **Going live**
   - Choose hosting platform
   - Deploy application
   - Set up monitoring
   - Plan marketing

---

**Installation Complete! Enjoy AcuMeds! 🎉**

For issues, refer to relevant section above or check documentation.
