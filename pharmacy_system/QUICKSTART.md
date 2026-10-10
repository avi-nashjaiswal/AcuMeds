# Quick Start Guide - AcuMeds Pharmacy System

## 5-Minute Setup Guide

### 1. Install Python Dependencies (1 min)

```bash
pip install -r requirements.txt
```

### 2. Initialize Database (1 min)

```bash
python database/db_init.py
```

This creates `database/pharmacy.db` with sample medicines and admin account.

### 3. Run the Application (1 min)

```bash
python run.py
```

Server starts at: `http://localhost:5000`

### 4. Login with Demo Account (1 min)

```
Email: admin@pharmacy.com
Password: admin123
```

### 5. Start Using the Application (1 min)

Visit these pages:
- Home: `http://localhost:5000/`
- Browse Medicines: `http://localhost:5000/medicines/`
- AI Recommendations: `http://localhost:5000/recommendations/`
- Admin Panel: `http://localhost:5000/admin/dashboard`

---

## User Workflow

### Step 1: Register or Login
- Click "Register" to create new account
- Or login with demo account

### Step 2: Browse Medicines
- Go to "Medicines" section
- Search by name or filter by category
- Click medicine to see details

### Step 3: Try AI Recommendations
- Click "AI Symptom Check"
- Enter your symptoms (e.g., "fever and cough")
- Get medicine recommendations
- Add recommended medicines to cart

### Step 4: Manage Cart
- Add medicines to cart from product pages
- Update quantities in cart
- View total price

### Step 5: Place Order
- Click "Checkout"
- Review order details
- Click "Place Order"
- View order confirmation

### Step 6: Track Orders
- Go to "Dashboard"
- View "Recent Orders" section
- Click order to see details and status

---

## Admin Workflow

### Access Admin Panel
- Login with admin account
- Click "Admin Panel" in navbar
- Or go to `http://localhost:5000/admin/dashboard`

### Manage Medicines
1. Click "Manage Medicines"
2. Add new: Click "Add New Medicine"
3. Edit: Click "Edit" button on medicine
4. Delete: Click "Delete" button (with confirmation)

### Manage Orders
1. Click "Manage Orders"
2. View all orders with customer details
3. Update status in dropdown:
   - Pending → Confirmed → Shipped → Delivered
4. Click order to see details

### View Dashboard
- Total medicines, orders, users, revenue
- Recent orders list
- Quick action buttons

---

## Test Data Included

### Sample Medicines (15 types)
```
Painkillers: Aspirin, Ibuprofen, Paracetamol
Antibiotics: Amoxicillin, Ciprofloxacin
Cold & Cough: Cough Syrup, Decongestant
Antacids: Omeprazole, Ranitidine
Vitamins: Vitamin C, Vitamin B Complex
Antihistamines: Cetirizine, Loratadine
Diabetes: Metformin, Insulin
```

### Categories
- Painkillers
- Antibiotics
- Cold & Cough
- Antacids
- Vitamins
- Antihistamines
- Diabetes

---

## Key Features to Try

### 1. Search Functionality
```
Go to: /medicines/
Search for: "aspirin", "fever", "antibiotic"
```

### 2. AI Recommendations
```
Go to: /recommendations/
Try symptoms: "fever", "cold and cough", "headache"
See confidence score and recommendations
```

### 3. Shopping Cart
```
Add medicines → Go to cart → Update quantities → Checkout
```

### 4. Order Tracking
```
Place order → View in order history → See status updates
```

### 5. Admin Controls
```
Add new medicine → Edit prices → Manage stock → Update order status
```

---

## Troubleshooting

### Issue: "Address already in use"
```bash
# Change port in run.py from 5000 to 5001
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Issue: "No module named 'flask'"
```bash
pip install -r requirements.txt
```

### Issue: "Database is locked"
```bash
# Delete pharmacy.db and reinitialize
python database/db_init.py
```

### Issue: Login doesn't work
```bash
# Make sure database was initialized
python database/db_init.py
# Use credentials: admin@pharmacy.com / admin123
```

### Issue: Static files not loading (CSS/JS)
Check folder structure - ensure these exist:
```
static/
├── css/
│   └── style.css
├── js/
│   └── main.js
└── uploads/
```

---

## File Locations

| File | Purpose |
|------|---------|
| `run.py` | Start application |
| `app/__init__.py` | Flask initialization |
| `app/routes.py` | All URL routes |
| `app/models.py` | Database models |
| `app/ai_recommendation.py` | AI engine |
| `database/db_init.py` | Initialize database |
| `database/pharmacy.db` | SQLite database |
| `templates/*.html` | HTML pages |
| `static/css/style.css` | Styling |
| `static/js/main.js` | JavaScript |

---

## API Endpoints Quick Reference

### Public Routes
- `GET /` - Home page
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /auth/logout` - User logout

### Authenticated Routes
- `GET /medicines/` - Browse medicines
- `GET /medicines/<id>` - Medicine details
- `POST /cart/add/<id>` - Add to cart
- `GET /cart/` - View cart
- `POST /orders/checkout` - Checkout
- `GET /orders/history` - Order history
- `POST /recommendations/get-recommendation` - Get recommendations
- `GET /profile` - User profile

### Admin Routes (is_admin required)
- `GET /admin/dashboard` - Admin dashboard
- `GET /admin/medicines` - Manage medicines
- `POST /admin/medicine/add` - Add medicine
- `POST /admin/medicine/<id>/edit` - Edit medicine
- `POST /admin/medicine/<id>/delete` - Delete medicine
- `GET /admin/orders` - Manage orders

---

## Configuration Changes

### Change Database
In `app/__init__.py`:
```python
# SQLite (default)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

# MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://user:password@localhost/pharmacy'

# PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost/pharmacy'
```

### Change Secret Key
In `app/__init__.py`:
```python
app.config['SECRET_KEY'] = 'your-new-secret-key'
```

### Change Max Upload Size
In `app/__init__.py`:
```python
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB
```

---

## Example Test Cases

### Test: Add Medicine to Cart and Checkout
1. Login as any user
2. Go to Medicines
3. Click on Aspirin
4. Enter quantity: 2
5. Click "Add to Cart"
6. Confirm message appears
7. Go to Cart
8. Click "Proceed to Checkout"
9. Click "Place Order"
10. See order confirmation

### Test: AI Recommendations
1. Go to AI Symptom Check
2. Enter: "I have high fever and cough"
3. Should show: Paracetamol, Ibuprofen, Cough Syrup
4. Click medicine to view details
5. Add to cart from recommendation page

### Test: Admin Adding Medicine
1. Login as admin
2. Go to Admin Panel
3. Click "Add Medicine"
4. Fill details:
   - Name: Test Medicine
   - Category: Painkillers
   - Price: 9.99
   - Stock: 100
5. Click Submit
6. Check medicines list - new medicine appears

---

## Development Tips

### Enable Debug Mode
Debug mode is already enabled in `run.py`:
```python
app.run(debug=True)
```

Changes to code automatically reload the server!

### View Database
Use SQLite browser or command line:
```bash
sqlite3 database/pharmacy.db
> SELECT * FROM medicines;
> SELECT * FROM users;
```

### Add More Sample Medicines
Edit `database/db_init.py` in the `add_sample_data()` function.

### Create New Routes
Add to `app/routes.py`:
```python
@some_bp.route('/new-route')
@login_required
def new_route():
    return render_template('new_template.html')
```

---

## Performance Tips

1. **Cache medicines**: Browser caches images/CSS
2. **Optimize database**: Add indexes (already done)
3. **Compress images**: Use optimized images
4. **Minimize CSS/JS**: For production

---

## Security Reminders

⚠️ **Before Production**:
- Change SECRET_KEY
- Set debug=False
- Use HTTPS
- Implement CSRF protection
- Add input validation
- Use environment variables for secrets
- Set up database backups

---

## Next Steps

1. ✅ Start the application
2. ✅ Register a new account
3. ✅ Browse medicines
4. ✅ Test AI recommendations
5. ✅ Place an order
6. ✅ Login as admin
7. ✅ Add/edit medicines
8. ✅ Update order status

---

**Happy coding! 🎉**

For detailed documentation, see [README.md](README.md)  
For AI system details, see [AI_SYSTEM.md](AI_SYSTEM.md)
