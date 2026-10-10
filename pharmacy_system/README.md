# AcuMeds - AI-Powered Online Pharmacy System

A complete web-based pharmacy management and medicine recommendation system built with Python Flask, SQLite, and modern web technologies.

## 📋 Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Technology Stack](#technology-stack)
- [Installation & Setup](#installation--setup)
- [Running the Application](#running-the-application)
- [Database Schema](#database-schema)
- [AI Recommendation System](#ai-recommendation-system)
- [API Endpoints](#api-endpoints)
- [Admin Features](#admin-features)
- [Demo Credentials](#demo-credentials)
- [Troubleshooting](#troubleshooting)

## ✨ Features

### User Features
- **User Authentication**: Secure registration and login system with password hashing
- **Medicine Catalog**: Browse medicines by category with search functionality
- **Shopping Cart**: Add medicines to cart, modify quantities, and view total
- **Order Management**: Place orders and track order history with status updates
- **AI Recommendations**: Get medicine suggestions based on symptom descriptions
- **User Profile**: Manage personal information and shipping address
- **Prescription Upload**: Upload prescription documents for verification

### Admin Features
- **Admin Dashboard**: Overview of medicines, orders, revenue, and users
- **Medicine Management**: Add, edit, and delete medicines from the inventory
- **Order Management**: View and update order status (Pending → Confirmed → Shipped → Delivered)
- **Inventory Tracking**: Monitor stock levels and medicine availability
- **Sales Reports**: Track revenue and order statistics

### AI Features
- **Symptom-Based Recommendations**: Rule-based NLP engine that recommends medicines based on user symptoms
- **Keyword Matching**: Recognizes common symptoms and maps them to appropriate medicines
- **Confidence Scoring**: Provides confidence score for recommendations
- **Recommendation History**: Stores user's past recommendations for reference

## 📁 Project Structure

```
pharmacy_system/
│
├── app/
│   ├── __init__.py           # Flask app initialization
│   ├── models.py             # Database models
│   ├── routes.py             # All route handlers
│   ├── ai_recommendation.py   # AI recommendation engine
│   └── forms.py              # Form definitions (optional)
│
├── database/
│   ├── schema.sql            # Database schema
│   ├── db_init.py           # Database initialization script
│   └── pharmacy.db          # SQLite database (generated)
│
├── templates/
│   ├── base.html            # Base template
│   ├── index.html           # Home page
│   ├── dashboard.html       # User dashboard
│   ├── profile.html         # User profile
│   ├── auth/
│   │   ├── login.html
│   │   └── register.html
│   ├── medicines/
│   │   ├── list.html
│   │   └── detail.html
│   ├── cart/
│   │   └── view.html
│   ├── order/
│   │   ├── checkout.html
│   │   ├── detail.html
│   │   └── history.html
│   ├── recommendation/
│   │   ├── form.html
│   │   ├── results.html
│   │   └── history.html
│   └── admin/
│       ├── dashboard.html
│       ├── medicines.html
│       ├── add_medicine.html
│       ├── edit_medicine.html
│       └── orders.html
│
├── static/
│   ├── css/
│   │   └── style.css        # Main stylesheet
│   ├── js/
│   │   └── main.js          # Main JavaScript
│   └── uploads/             # User uploaded files
│
├── run.py                    # Application entry point
├── requirements.txt          # Python dependencies
└── README.md                 # This file

```

## 🛠 Technology Stack

### Backend
- **Framework**: Flask 2.3.0
- **Database**: SQLite3 (easily switchable to MySQL/PostgreSQL)
- **ORM**: SQLAlchemy
- **Authentication**: Flask-Login with password hashing (Werkzeug)
- **Python Version**: 3.8+

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Custom styling + Bootstrap 5.3
- **JavaScript**: Vanilla JS for interactivity
- **Bootstrap**: Responsive design framework
- **FontAwesome**: Icon library

### AI/ML
- **NLP Approach**: Rule-based keyword matching
- **Symptom Mapping**: Dictionary-based medicine recommendations
- **Confidence Scoring**: Statistical relevance calculation

## 📦 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git (optional)

### Step 1: Clone or Download the Project

```bash
cd pharmacy_system
```

### Step 2: Create Virtual Environment (Recommended)

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**On MacOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Initialize Database

The database will be automatically initialized when you first run the application. If you want to manually initialize it:

```bash
python
>>> from database.db_init import init_db
>>> init_db()
```

### Step 5: Configuration

Edit `app/__init__.py` to change the SECRET_KEY for production:

```python
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
```

## 🚀 Running the Application

### Start the Flask Development Server

```bash
python run.py
```

The application will start at `http://localhost:5000`

### Access the Application

- **Home Page**: http://localhost:5000/
- **Login**: http://localhost:5000/auth/login
- **Register**: http://localhost:5000/auth/register
- **Admin Panel**: http://localhost:5000/admin/dashboard

## 🗄 Database Schema

### Users Table
- id (Primary Key)
- username (Unique)
- email (Unique)
- password_hash
- full_name
- phone
- address
- created_at
- is_admin (Boolean)

### Medicines Table
- id (Primary Key)
- name
- category
- description
- price
- stock_quantity
- requires_prescription (Boolean)
- side_effects
- usage_instructions
- created_at

### Orders Table
- id (Primary Key)
- user_id (Foreign Key)
- order_date
- total_amount
- status (Pending, Confirmed, Shipped, Delivered)
- estimated_delivery_date

### Order Items Table
- id (Primary Key)
- order_id (Foreign Key)
- medicine_id (Foreign Key)
- quantity
- price_at_purchase

### Cart Items Table
- id (Primary Key)
- user_id (Foreign Key)
- medicine_id (Foreign Key)
- quantity
- added_at

### Prescriptions Table
- id (Primary Key)
- user_id (Foreign Key)
- file_path
- uploaded_at
- verified (Boolean)

### Recommendations Table
- id (Primary Key)
- user_id (Foreign Key)
- symptoms (Text)
- recommended_medicines (JSON format)
- recommendation_date

## 🤖 AI Recommendation System

### How It Works

The AI recommendation system uses a **rule-based keyword matching algorithm**:

1. **Symptom Input**: User enters their symptoms in natural English
2. **Keyword Extraction**: System extracts keywords from the input
3. **Symptom Mapping**: Maps keywords to predefined symptom categories
4. **Medicine Recommendation**: Retrieves medicines associated with matched symptoms
5. **Ranking**: Sorts recommendations by relevance based on match count
6. **Confidence Score**: Calculates confidence based on symptom matches

### Example Symptoms Recognized

```
Cold → Cough Syrup, Decongestant, Vitamin C
Fever → Paracetamol, Ibuprofen, Aspirin
Headache → Aspirin, Paracetamol, Ibuprofen
Heartburn → Omeprazole, Ranitidine
Allergy → Cetirizine, Loratadine
And many more...
```

### Code Structure

**File**: `app/ai_recommendation.py`

```python
class MedicineRecommendationEngine:
    SYMPTOM_MEDICINE_MAP = {
        'symptom_keyword': [
            {'name': 'Medicine Name', 'category': 'Category', 'reason': 'Why recommended'},
            ...
        ]
    }
    
    @staticmethod
    def get_recommendations(symptoms_text):
        # Returns: {
        #     'recommendations': [...],
        #     'symptoms_matched': [...],
        #     'confidence': float,
        #     'message': str
        # }
```

### Adding New Symptoms

To add new symptom-medicine mappings, edit `SYMPTOM_MEDICINE_MAP` in `app/ai_recommendation.py`:

```python
'new_symptom': [
    {
        'name': 'Medicine Name',
        'category': 'Category',
        'reason': 'Why this medicine helps'
    }
]
```

## 🔐 Authentication & Security

- **Password Hashing**: Uses Werkzeug's `generate_password_hash` and `check_password_hash`
- **Session Management**: Flask-Login handles user sessions
- **Login Required**: Protected routes use `@login_required` decorator
- **Admin Access**: Admin routes check `current_user.is_admin` flag
- **CSRF Protection**: Should be implemented for production

## 📊 API Endpoints

### Authentication
- `GET /auth/login` - Login page
- `POST /auth/login` - Process login
- `GET /auth/register` - Registration page
- `POST /auth/register` - Process registration
- `GET /auth/logout` - Logout user

### Medicines
- `GET /medicines/` - List all medicines
- `GET /medicines/<id>` - Medicine details
- `GET /medicines/?search=query` - Search medicines
- `GET /medicines/?category=name` - Filter by category

### Shopping Cart
- `GET /cart/` - View cart
- `POST /cart/add/<medicine_id>` - Add to cart
- `POST /cart/remove/<item_id>` - Remove from cart
- `POST /cart/update/<item_id>` - Update quantity

### Orders
- `GET /orders/` - Checkout page
- `POST /orders/` - Place order
- `GET /orders/<order_id>` - Order details
- `GET /orders/history` - Order history

### AI Recommendations
- `GET /recommendations/` - Recommendation form
- `POST /recommendations/get-recommendation` - Get recommendations
- `GET /recommendations/history` - Recommendation history

### Admin
- `GET /admin/dashboard` - Admin dashboard
- `GET /admin/medicines` - Manage medicines
- `GET /admin/medicine/add` - Add medicine form
- `POST /admin/medicine/add` - Process add medicine
- `GET /admin/medicine/<id>/edit` - Edit medicine form
- `POST /admin/medicine/<id>/edit` - Process edit medicine
- `POST /admin/medicine/<id>/delete` - Delete medicine
- `GET /admin/orders` - Manage orders
- `POST /admin/order/<id>/status` - Update order status

## 👨‍💼 Admin Features

### Admin Login
- **Email**: admin@pharmacy.com
- **Password**: admin123

### Admin Dashboard
Shows statistics:
- Total medicines
- Total orders
- Total users
- Total revenue
- Recent orders list

### Medicine Management
- Add new medicines
- Edit medicine details
- Update prices and stock
- Delete medicines
- Manage prescription requirements

### Order Management
- View all orders
- Update order status
- Track order details
- View customer information

## 💳 Demo Credentials

### Admin Account
```
Email: admin@pharmacy.com
Password: admin123
```

### Sample Medicines Included
- Painkillers: Aspirin, Ibuprofen, Paracetamol
- Antibiotics: Amoxicillin, Ciprofloxacin
- Cold & Cough: Cough Syrup, Decongestant
- Antacids: Omeprazole, Ranitidine
- Vitamins: Vitamin C, Vitamin B Complex
- Antihistamines: Cetirizine, Loratadine
- Diabetes: Metformin, Insulin

## 🐛 Troubleshooting

### Issue: Module not found errors
**Solution**: Make sure you've installed all requirements:
```bash
pip install -r requirements.txt
```

### Issue: Database file not found
**Solution**: Create the database manually:
```bash
python database/db_init.py
```

### Issue: Port 5000 already in use
**Solution**: Change the port in `run.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Issue: Login not working
**Solution**: Ensure the database is initialized with sample data:
```bash
python database/db_init.py
```

### Issue: Static files not loading
**Solution**: Ensure the `static/` folder exists with correct structure:
```
static/
├── css/
│   └── style.css
├── js/
│   └── main.js
└── uploads/
```

## 📝 Development Notes

### Adding New Features

1. **Database Changes**: Update `database/schema.sql` and create migrations
2. **New Routes**: Add to appropriate blueprint in `app/routes.py`
3. **Templates**: Create in `templates/` with proper folder structure
4. **Styling**: Add CSS to `static/css/style.css`

### Code Comments

All code includes detailed comments explaining:
- Function purposes
- Parameter descriptions
- Return values
- Implementation logic

## 📄 License

This project is open source and available for educational purposes.

## 🤝 Contributing

To contribute to this project:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📧 Support

For issues and questions:
- Review the Troubleshooting section
- Check code comments for implementation details
- Verify all files are in correct locations

## 🎯 Future Enhancements

Potential improvements:
- Payment gateway integration (Stripe, PayPal)
- Email notifications
- SMS OTP verification
- Advanced search with filters
- Medicine reviews and ratings
- Prescription verification system
- Inventory management alerts
- Advanced AI models (TensorFlow, PyTorch)
- Mobile app version
- Multi-language support

## ⭐ Features Checklist

✅ User Registration and Login
✅ Medicine Catalog and Search
✅ Shopping Cart System
✅ Order Placement and Tracking
✅ AI-Based Recommendations
✅ Admin Dashboard
✅ Medicine Management
✅ Order Management
✅ User Profile Management
✅ Responsive Design
✅ Security Features
✅ Database Integration

---

**Version**: 1.0.0  
**Last Updated**: 2024  
**Author**: AcuMeds Development Team
