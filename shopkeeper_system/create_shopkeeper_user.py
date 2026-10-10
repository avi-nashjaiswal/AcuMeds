# Script to create a new shopkeeper user directly in the database
from app import create_app, db
from app.models import User, Shopkeeper

app = create_app()

with app.app_context():
    # ---- CHANGE THESE VALUES ----
    username = 'usernameajay89'
    email = 'emailajay23@gmail.com'
    password = '321456'
    full_name = 'Ajay Medical'
    shop_name = 'Ajay Medical'
    license_number = 'LIC987654'
    contact_number = '9876543210'
    # -----------------------------

    # Check if user exists
    if User.query.filter_by(username=username).first():
        print('Username already exists')
        exit(1)
    if User.query.filter_by(email=email).first():
        print('Email already exists')
        exit(1)

    user = User(
        username=username,
        email=email,
        full_name=full_name,
        phone=contact_number
    )
    user.set_password(password)
    db.session.add(user)
    db.session.flush()

    shopkeeper = Shopkeeper(
        user_id=user.id,
        shop_name=shop_name,
        license_number=license_number,
        contact_number=contact_number
    )
    db.session.add(shopkeeper)
    db.session.commit()
    print('Shopkeeper user created successfully!')
