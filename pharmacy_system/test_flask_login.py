from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    # Clear any cached sessions
    db.session.remove()
    
    print("Testing customer1 login...")
    user = User.query.filter_by(username='customer1').first()
    
    if user:
        print(f"✅ User found: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Role: {user.role}")
        print(f"   Password check: {user.check_password('customer123')}")
    else:
        print("❌ User NOT found in Flask app")
        
        # List all users
        print("\nAll users in Flask:")
        all_users = User.query.all()
        for u in all_users:
            print(f"  - {u.username}")
