"""
Routes for Shopkeeper App
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from functools import wraps
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from app import db
from app.models import User, Medicine, Shopkeeper, Order, OrderItem, MedicineRating, Notification
from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta
import os
import json
import shutil
import sqlite3
import requests
import uuid
from app.localization import get_language_label, set_current_language, translate as t

# Upload settings
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'avif', 'jfif'}
UPLOAD_SUBDIR = 'medicines'

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_upload_roots():
    """Build upload roots for shopkeeper, pharmacy, and admin apps"""
    app_upload_root = current_app.config.get('UPLOAD_FOLDER')
    if not app_upload_root:
        app_upload_root = os.path.join(current_app.root_path, 'static', 'uploads')

    project_root = os.path.abspath(os.path.join(current_app.root_path, os.pardir, os.pardir))
    upload_roots = [app_upload_root]
    for app_dir in ('pharmacy_system', 'admin_system'):
        candidate = os.path.join(project_root, app_dir, 'static', 'uploads')
        if candidate not in upload_roots:
            upload_roots.append(candidate)

    return upload_roots

def save_medicine_image(file, medicine_id, sequence=None):
    """Save medicine image and return path"""
    if file and allowed_file(file.filename):
        upload_roots = get_upload_roots()
        if not upload_roots:
            return None

        # Generate unique filename
        safe_name = secure_filename(file.filename) or 'image'
        unique_key = f"{sequence}_{uuid.uuid4().hex[:8]}" if sequence is not None else uuid.uuid4().hex[:8]
        filename = f"medicine_{medicine_id}_{unique_key}_{safe_name}"

        primary_root = upload_roots[0]
        primary_dir = os.path.join(primary_root, UPLOAD_SUBDIR)
        os.makedirs(primary_dir, exist_ok=True)
        primary_path = os.path.join(primary_dir, filename)

        # Save file to primary location
        file.save(primary_path)

        # Copy file to other app upload folders
        for extra_root in upload_roots[1:]:
            extra_dir = os.path.join(extra_root, UPLOAD_SUBDIR)
            os.makedirs(extra_dir, exist_ok=True)
            shutil.copy2(primary_path, os.path.join(extra_dir, filename))

        # Return path relative to static folder
        return f"uploads/{UPLOAD_SUBDIR}/{filename}"
    return None


def save_medicine_gallery(files, medicine_id):
    """Save multiple uploaded images and return relative paths."""
    saved = []
    for idx, file in enumerate(files or [], start=1):
        if file and file.filename and allowed_file(file.filename):
            path = save_medicine_image(file, medicine_id, sequence=idx)
            if path:
                saved.append(path)
    return saved

def _sync_order_status_to_shared_dbs(order_id, status, delivery_date=None):
    project_root = os.path.abspath(os.path.join(current_app.root_path, os.pardir, os.pardir))
    db_paths = [
        os.path.join(project_root, 'admin_system', 'database', 'pharmacy.db'),
        os.path.join(project_root, 'pharmacy_system', 'database', 'pharmacy.db'),
    ]

    delivery_value = None
    if delivery_date:
        delivery_value = delivery_date.isoformat(sep=' ', timespec='seconds')
    updated_value = datetime.utcnow().isoformat(sep=' ', timespec='seconds')

    for db_path in db_paths:
        if not os.path.exists(db_path):
            continue
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='orders'")
            if not cur.fetchone():
                conn.close()
                continue
            cur.execute("PRAGMA table_info(orders)")
            cols = {row[1] for row in cur.fetchall()}
            if 'status' not in cols:
                conn.close()
                continue

            updates = ["status = ?"]
            params = [status]
            if status == 'Delivered' and 'delivery_date' in cols and delivery_value:
                updates.append("delivery_date = ?")
                params.append(delivery_value)
            if 'updated_at' in cols:
                updates.append("updated_at = ?")
                params.append(updated_value)

            params.append(order_id)
            cur.execute(f"UPDATE orders SET {', '.join(updates)} WHERE id = ?", params)
            conn.commit()
            conn.close()
        except Exception:
            continue

# Custom decorator for shopkeeper-only routes (prevents redirect loops)
def shopkeeper_required(f):
    """Decorator to require shopkeeper authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check authentication
        if not current_user.is_authenticated:
            flash(t('messages.login_required'), 'warning')
            return redirect(url_for('auth.login'))
        
        # Make session permanent (long-lived)
        session.permanent = True
        session.modified = True
        
        try:
            # Check if user has a shopkeeper profile
            shopkeeper = Shopkeeper.query.filter_by(user_id=current_user.id).first()
            if not shopkeeper:
                flash(t('messages.shopkeeper_profile_missing'), 'danger')
                logout_user()
                return redirect(url_for('auth.login'))
        except Exception as e:
            # Database error - keep user logged in but show error
            print(f"Database error in shopkeeper_required: {str(e)}")
            flash(t('messages.database_error'), 'danger')
            return redirect(url_for('auth.login'))
        
        return f(*args, **kwargs)
    
    return decorated_function

# ==================== AUTH BLUEPRINT ====================
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Shopkeeper login - Independent system, no admin dependency"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        # Try to find user by email or username
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User.query.filter_by(username=email).first()
        
        if user and user.check_password(password):
            # Verify shopkeeper profile exists
            shopkeeper = Shopkeeper.query.filter_by(user_id=user.id).first()
            if not shopkeeper:
                flash(t('messages.shopkeeper_profile_missing'), 'danger')
                return redirect(url_for('auth.login'))
            
            # Make session permanent (long-lived)
            login_user(user, remember=True)
            session.permanent = True
            session.modified = True
            
            flash(t('messages.welcome_user', name=user.full_name or user.username), 'success')
            return redirect(url_for('dashboard.index'))
        
        flash(t('messages.invalid_credentials'), 'danger')
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Shopkeeper registration - Direct registration, no admin approval needed"""
    if request.method == 'POST':
        try:
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '').strip()
            full_name = request.form.get('full_name', '').strip()
            shop_name = request.form.get('shop_name', '').strip()
            license_number = request.form.get('license_number', '').strip()
            contact_number = request.form.get('contact_number', '').strip()
            
            # Validation
            if not all([username, email, password, full_name, shop_name, license_number, contact_number]):
                flash(t('messages.fill_required_fields'), 'danger')
                return redirect(url_for('auth.register'))
            
            # Check if user exists
            if User.query.filter_by(username=username).first():
                flash(t('messages.username_exists'), 'danger')
                return redirect(url_for('auth.register'))
            
            if User.query.filter_by(email=email).first():
                flash(t('messages.email_exists'), 'danger')
                return redirect(url_for('auth.register'))
            
            # Create shopkeeper user
            user = User(
                username=username,
                email=email,
                full_name=full_name,
                phone=contact_number
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.flush()
            
            # Create shopkeeper profile
            shopkeeper = Shopkeeper(
                user_id=user.id,
                shop_name=shop_name,
                license_number=license_number,
                contact_number=contact_number
            )
            db.session.add(shopkeeper)
            db.session.commit()
            
            flash(t('messages.registration_successful'), 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            print(f'Registration error: {str(e)}')
            flash(t('messages.registration_failed', error=str(e)), 'danger')
            return redirect(url_for('auth.register'))
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
def logout():
    """Logout"""
    logout_user()
    flash(t('messages.logged_out'), 'info')
    return redirect(url_for('auth.login'))



# ==================== DASHBOARD BLUEPRINT ====================
dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/language/<language_code>')
def set_language(language_code):
    """Persist the selected language and return to the previous page."""
    chosen_language = set_current_language(language_code)
    flash(t('messages.language_changed', language=get_language_label(chosen_language)), 'success')
    next_url = request.args.get('next') or request.referrer or url_for('dashboard.index')
    return redirect(next_url)


def _build_local_ai_answer(question, page):
    """Fallback helper when external AI service is unavailable."""
    question_text = (question or '').strip().lower()
    page_text = (page or '').strip().lower()

    if question_text in {'hi', 'hello', 'hey'} or question_text.startswith(('hi ', 'hello ', 'hey ')):
        return (
            'Hi! I can help with medicines, orders, and profile updates. '
            'Tell me what you want to do on this page.'
        )

    if 'order' in question_text or 'order' in page_text:
        return (
            'For orders, open the Orders section from the dashboard. '
            'Use the action buttons to confirm, reject, or update delivery status.'
        )

    if any(word in question_text for word in ('medicine', 'stock', 'inventory', 'price')):
        return (
            'For medicine updates, go to Medicines and edit stock, price, or expiry details, '
            'then save the form.'
        )

    if any(word in question_text for word in ('profile', 'account', 'shop')):
        return (
            'Use the Profile page to update shop information, contact details, city, and password.'
        )

    return (
        'AI is running in basic help mode right now. '
        'Ask about orders, medicines, or profile steps and I will guide you.'
    )

@dashboard_bp.route('/ai-bot', methods=['POST'])
def ai_bot():
    """Return AI assistant answer using the current page context and user question."""
    data = request.get_json(silent=True) or {}
    question = (data.get('question') or '').strip()
    page = (data.get('page') or '').strip()

    if not question:
        return jsonify({'answer': 'Please type a question first.'}), 400

    openai_api_key = (current_app.config.get('OPENAI_API_KEY') or os.environ.get('OPENAI_API_KEY') or '').strip()
    if not openai_api_key:
        return jsonify({'answer': _build_local_ai_answer(question, page)}), 200

    model_name = (current_app.config.get('OPENAI_MODEL') or os.environ.get('OPENAI_MODEL') or 'gpt-4o-mini').strip() or 'gpt-4o-mini'

    prompt = f"Page: {page}\nUser question: {question}\nAnswer in simple language."
    try:
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {openai_api_key}',
                'Content-Type': 'application/json'
            },
            json={
                'model': model_name,
                'messages': [
                    {'role': 'system', 'content': 'You are a helpful assistant for a medical shop web app.'},
                    {'role': 'user', 'content': prompt}
                ],
                'max_tokens': 200
            },
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        answer = (
            result.get('choices', [{}])[0]
            .get('message', {})
            .get('content', '')
            .strip()
        )
        if not answer:
            answer = _build_local_ai_answer(question, page)
    except Exception:
        answer = _build_local_ai_answer(question, page)

    return jsonify({'answer': answer})

# Profile route for shopkeeper
@dashboard_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    shopkeeper = Shopkeeper.query.filter_by(user_id=current_user.id).first()
    if not shopkeeper:
        flash('Shopkeeper profile not found.', 'danger')
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        # Update profile fields
        shopkeeper.shop_name = request.form.get('shop_name', shopkeeper.shop_name)
        shopkeeper.license_number = request.form.get('license_number', shopkeeper.license_number)
        shopkeeper.contact_number = request.form.get('contact_number', shopkeeper.contact_number)
        shopkeeper.city = request.form.get('city', shopkeeper.city)
        current_user.full_name = request.form.get('full_name', current_user.full_name)
        current_user.phone = request.form.get('phone', current_user.phone)
        # Password change (optional)
        new_password = request.form.get('password', '')
        if new_password:
            current_user.set_password(new_password)
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('dashboard.profile'))

    return render_template('dashboard/profile.html', shopkeeper=shopkeeper, user=current_user)

@dashboard_bp.route('/pending-verification')
@shopkeeper_required
def pending_verification():
    """Show verification pending page"""
    shopkeeper = Shopkeeper.query.filter_by(user_id=current_user.id).first()
    
    if shopkeeper.verified:
        return redirect(url_for('dashboard.index'))
    
    return render_template('dashboard/pending_verification.html', shopkeeper=shopkeeper)

@dashboard_bp.route('/')
@shopkeeper_required
def index():
    """Shopkeeper dashboard"""
    shopkeeper = Shopkeeper.query.filter_by(user_id=current_user.id).first()
    
    # Check if verified
    if not shopkeeper.verified:
        return redirect(url_for('dashboard.pending_verification'))
    
    # Get shopkeeper's medicines
    medicines = Medicine.query.filter_by(shopkeeper_id=shopkeeper.id).all()
    
    # Calculate stats
    total_medicines = len(medicines)
    total_stock = sum(m.stock_quantity for m in medicines)
    total_revenue = 0
    
    # Get orders for this shopkeeper's medicines
    orders_list = db.session.query(Order).join(OrderItem).join(Medicine).filter(
        Medicine.shopkeeper_id == shopkeeper.id
    ).options(joinedload(Order.user)).distinct().all()
    
    for order in orders_list:
        total_revenue += order.total_amount
    
    return render_template('dashboard/index.html',
                         shopkeeper=shopkeeper,
                         medicines=medicines,
                         total_medicines=total_medicines,
                         total_stock=total_stock,
                         total_revenue=total_revenue,
                         orders_count=len(orders_list))

@dashboard_bp.route('/medicines')
@shopkeeper_required
def medicines():
    """View all shop medicines"""
    shopkeeper = Shopkeeper.query.filter_by(user_id=current_user.id).first()
    
    # Check if verified
    if not shopkeeper.verified:
        return redirect(url_for('dashboard.pending_verification'))
    
    medicines = Medicine.query.filter_by(shopkeeper_id=shopkeeper.id).all()
    
    return render_template('dashboard/medicines.html', medicines=medicines, shopkeeper=shopkeeper)


@dashboard_bp.route('/inventory')
@shopkeeper_required
def inventory():
    """Inventory management dashboard"""
    shopkeeper = Shopkeeper.query.filter_by(user_id=current_user.id).first()
    
    return render_template('dashboard/inventory.html', shopkeeper=shopkeeper)

@dashboard_bp.route('/add-medicine', methods=['GET', 'POST'])
@shopkeeper_required
def add_medicine():
    """Add new medicine"""
    shopkeeper = Shopkeeper.query.filter_by(user_id=current_user.id).first()
    
    # Check if verified
    if not shopkeeper.verified:
        flash('Your shop must be verified before you can add medicines.', 'warning')
        return redirect(url_for('dashboard.pending_verification'))
    
    if request.method == 'POST':
        strength_value = None
        strength_value_raw = request.form.get('strength_value', '').strip()
        if strength_value_raw:
            try:
                strength_value = float(strength_value_raw)
            except ValueError:
                flash('Strength value must be a number.', 'warning')
        strength_unit = request.form.get('strength_unit', '').strip() or None

        medicine = Medicine(
            name=request.form.get('name'),
            category=request.form.get('category'),
            description=request.form.get('description'),
            strength_value=strength_value,
            strength_unit=strength_unit,
            price=float(request.form.get('price', 0)),
            stock_quantity=int(request.form.get('stock_quantity', 0)),
            requires_prescription=request.form.get('requires_prescription') == 'on',
            side_effects=request.form.get('side_effects'),
            usage_instructions=request.form.get('usage_instructions'),
            shopkeeper_id=shopkeeper.id
        )
        
        # Add medicine to database first to get the ID
        db.session.add(medicine)
        db.session.flush()
        
        # Handle multiple image uploads
        image_files = request.files.getlist('medicine_images')
        if not any(f and f.filename for f in image_files):
            # Backward compatibility with old input name
            image_files = request.files.getlist('medicine_image')

        invalid_files = [f.filename for f in image_files if f and f.filename and not allowed_file(f.filename)]
        if invalid_files:
            flash('Some files were skipped due to unsupported format.', 'warning')

        gallery_paths = save_medicine_gallery(image_files, medicine.id)
        if gallery_paths:
            medicine.set_gallery_images(gallery_paths)
        else:
            gallery_order_raw = request.form.get('gallery_order', '').strip()
            if gallery_order_raw:
                try:
                    gallery_order = json.loads(gallery_order_raw)
                except (TypeError, ValueError, json.JSONDecodeError):
                    gallery_order = None

                if isinstance(gallery_order, list):
                    current_gallery = medicine.get_gallery_images()
                    reordered_gallery = []
                    for image_path in gallery_order:
                        if image_path in current_gallery and image_path not in reordered_gallery:
                            reordered_gallery.append(image_path)

                    if reordered_gallery:
                        medicine.set_gallery_images(reordered_gallery)

        db.session.commit()
        
        flash(f'Medicine "{medicine.name}" added successfully!', 'success')
        return redirect(url_for('dashboard.medicines'))
    
    return render_template('dashboard/add_medicine.html')

@dashboard_bp.route('/edit-medicine/<int:med_id>', methods=['GET', 'POST'])
@shopkeeper_required
def edit_medicine(med_id):
    """Edit medicine"""
    medicine = Medicine.query.get_or_404(med_id)
    shopkeeper = Shopkeeper.query.filter_by(user_id=current_user.id).first()
    
    if not shopkeeper or medicine.shopkeeper_id != shopkeeper.id:
        flash('You can only edit your own medicines.', 'danger')
        return redirect(url_for('dashboard.medicines'))
    
    if request.method == 'POST':
        medicine.name = request.form.get('name')
        medicine.category = request.form.get('category')
        medicine.description = request.form.get('description')
        strength_value_raw = request.form.get('strength_value', '').strip()
        if strength_value_raw:
            try:
                medicine.strength_value = float(strength_value_raw)
            except ValueError:
                flash('Strength value must be a number.', 'warning')
        else:
            medicine.strength_value = None
        medicine.strength_unit = request.form.get('strength_unit', '').strip() or None
        medicine.price = float(request.form.get('price', 0))
        medicine.stock_quantity = int(request.form.get('stock_quantity', 0))
        medicine.requires_prescription = request.form.get('requires_prescription') == 'on'
        medicine.side_effects = request.form.get('side_effects')
        medicine.usage_instructions = request.form.get('usage_instructions')
        
        # Handle multiple image uploads (replaces current gallery)
        image_files = request.files.getlist('medicine_images')
        if not any(f and f.filename for f in image_files):
            # Backward compatibility with old input name
            image_files = request.files.getlist('medicine_image')

        invalid_files = [f.filename for f in image_files if f and f.filename and not allowed_file(f.filename)]
        if invalid_files:
            flash('Some files were skipped due to unsupported format.', 'warning')

        gallery_paths = save_medicine_gallery(image_files, medicine.id)
        if gallery_paths:
            medicine.set_gallery_images(gallery_paths)
        else:
            gallery_order_raw = request.form.get('gallery_order', '').strip()
            if gallery_order_raw:
                try:
                    gallery_order = json.loads(gallery_order_raw)
                except (TypeError, ValueError, json.JSONDecodeError):
                    gallery_order = None

                if isinstance(gallery_order, list):
                    current_gallery = medicine.get_gallery_images()
                    reordered_gallery = []
                    for image_path in gallery_order:
                        if image_path in current_gallery and image_path not in reordered_gallery:
                            reordered_gallery.append(image_path)

                    if reordered_gallery:
                        medicine.set_gallery_images(reordered_gallery)
        
        db.session.commit()
        flash('Medicine updated successfully!', 'success')
        return redirect(url_for('dashboard.medicines'))
    
    return render_template('dashboard/edit_medicine.html', medicine=medicine, gallery_images=medicine.get_gallery_images())

@dashboard_bp.route('/delete-medicine/<int:med_id>', methods=['POST'])
@shopkeeper_required
def delete_medicine(med_id):
    """Delete medicine"""
    medicine = Medicine.query.get_or_404(med_id)
    shopkeeper = Shopkeeper.query.filter_by(user_id=current_user.id).first()
    
    if not shopkeeper or medicine.shopkeeper_id != shopkeeper.id:
        flash('You can only delete your own medicines.', 'danger')
        return redirect(url_for('dashboard.medicines'))
    
    med_name = medicine.name
    db.session.delete(medicine)
    db.session.commit()
    flash(f'Medicine "{med_name}" deleted successfully!', 'success')
    return redirect(url_for('dashboard.medicines'))

@dashboard_bp.route('/orders')
@shopkeeper_required
def orders():
    """View shop orders"""
    shopkeeper = Shopkeeper.query.filter_by(user_id=current_user.id).first()
    
    # Check if verified
    if not shopkeeper.verified:
        return redirect(url_for('dashboard.pending_verification'))
    
    # Get orders containing this shopkeeper's medicines
    orders_list = db.session.query(Order).join(OrderItem).join(Medicine).filter(
        Medicine.shopkeeper_id == shopkeeper.id
    ).distinct().all()
    
    return render_template('dashboard/orders.html', orders=orders_list, shopkeeper=shopkeeper)


@dashboard_bp.route('/notifications')
@shopkeeper_required
def notifications():
    """View notifications for the current shopkeeper"""
    unread_notes = Notification.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).all()

    if unread_notes:
        for note in unread_notes:
            note.is_read = True
        db.session.commit()

    notes = Notification.query.filter_by(user_id=current_user.id).order_by(
        Notification.created_at.desc()
    ).all()
    return render_template('dashboard/notifications.html', notifications=notes)


@dashboard_bp.route('/ratings')
@shopkeeper_required
def ratings():
    """View ratings for the shopkeeper's medicines"""
    shopkeeper = Shopkeeper.query.filter_by(user_id=current_user.id).first()

    if not shopkeeper.verified:
        return redirect(url_for('dashboard.pending_verification'))

    ratings_list = MedicineRating.query.join(Medicine).filter(
        Medicine.shopkeeper_id == shopkeeper.id
    ).options(
        joinedload(MedicineRating.user),
        joinedload(MedicineRating.medicine),
        joinedload(MedicineRating.order_item).joinedload(OrderItem.order)
    ).order_by(MedicineRating.created_at.desc()).all()

    avg_rating = db.session.query(db.func.avg(MedicineRating.rating)).join(Medicine).filter(
        Medicine.shopkeeper_id == shopkeeper.id
    ).scalar() or 0

    return render_template('dashboard/ratings.html',
                           ratings=ratings_list,
                           total_ratings=len(ratings_list),
                           avg_rating=round(avg_rating, 2),
                           shopkeeper=shopkeeper)


@dashboard_bp.route('/orders/<int:order_id>/status', methods=['POST'])
@shopkeeper_required
def update_order_status(order_id):
    """Shopkeeper updates order status (Delivered)"""
    shopkeeper = Shopkeeper.query.filter_by(user_id=current_user.id).first()
    if not shopkeeper or not shopkeeper.verified:
        flash('Unauthorized', 'danger')
        return redirect(url_for('dashboard.orders'))

    order = Order.query.get_or_404(order_id)

    # Verify the order contains this shopkeeper's medicines
    has_access = db.session.query(OrderItem.id).join(Medicine).filter(
        OrderItem.order_id == order.id,
        Medicine.shopkeeper_id == shopkeeper.id
    ).first()
    if not has_access:
        flash('Unauthorized', 'danger')
        return redirect(url_for('dashboard.orders'))

    if order.status in {'Delivered', 'Cancelled'}:
        flash(f'Order #{order.id} is already {order.status.lower()}.', 'info')
        return redirect(url_for('dashboard.orders'))

    new_status = (request.form.get('status') or '').strip()
    allowed_statuses = {'Ready', 'Shipped', 'Delivered', 'Cancelled'}
    if new_status not in allowed_statuses:
        flash('Invalid status update.', 'warning')
        return redirect(url_for('dashboard.orders'))

    cancellable_statuses = {'Pending', 'Confirmed', 'Ready'}
    if new_status == 'Cancelled' and order.status not in cancellable_statuses:
        flash('Order cannot be cancelled at this stage.', 'warning')
        return redirect(url_for('dashboard.orders'))

    order.status = new_status
    if new_status == 'Delivered':
        order.delivery_date = datetime.utcnow()
    order.updated_at = datetime.utcnow()

    if new_status == 'Cancelled':
        db.session.add(Notification(
            user_id=order.user_id,
            title='Order Cancelled',
            message=f'Your order #{order.id} has been cancelled by the shopkeeper.',
            notification_type='order_cancelled',
            related_order_id=order.id
        ))

    db.session.commit()
    _sync_order_status_to_shared_dbs(order.id, new_status, order.delivery_date)
    if new_status == 'Cancelled':
        flash(f'Order #{order.id} cancelled.', 'success')
    else:
        flash(f'Order #{order.id} updated to {new_status}.', 'success')
    return redirect(url_for('dashboard.orders'))


# ==================== INVENTORY MANAGEMENT API ====================
api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/inventory', methods=['GET'])
@shopkeeper_required
def get_inventory():
    """Get all inventory items for this shopkeeper"""
    try:
        shopkeeper = Shopkeeper.query.filter_by(user_id=current_user.id).first()
        
        medicines = Medicine.query.filter_by(shopkeeper_id=shopkeeper.id).all()
        
        inventory_items = [
            {
                'id': m.id,
                'name': m.name,
                'category': m.category,
                'price': float(m.price),
                'stock_quantity': m.stock_quantity,
                'requires_prescription': m.requires_prescription,
                'low_stock': m.stock_quantity < 10,  # Threshold: 10 units
                'image': m.image
            }
            for m in medicines
        ]
        
        return jsonify({
            'success': True,
            'count': len(inventory_items),
            'inventory': inventory_items
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/inventory/<int:medicine_id>', methods=['GET'])
@shopkeeper_required
def get_inventory_item(medicine_id):
    """Get details of a specific medicine"""
    try:
        shopkeeper = Shopkeeper.query.filter_by(user_id=current_user.id).first()
        medicine = Medicine.query.get_or_404(medicine_id)
        
        if not shopkeeper or medicine.shopkeeper_id != shopkeeper.id:
            return jsonify({'error': 'Access denied'}), 403
        
        return jsonify({
            'success': True,
            'medicine': {
                'id': medicine.id,
                'name': medicine.name,
                'category': medicine.category,
                'description': medicine.description,
                'price': float(medicine.price),
                'stock_quantity': medicine.stock_quantity,
                'requires_prescription': medicine.requires_prescription,
                'side_effects': medicine.side_effects,
                'usage_instructions': medicine.usage_instructions,
                'image': medicine.image
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/inventory/<int:medicine_id>/update-stock', methods=['PATCH'])
@shopkeeper_required
def update_stock(medicine_id):
    """Update stock quantity for a medicine"""
    try:
        shopkeeper = Shopkeeper.query.filter_by(user_id=current_user.id).first()
        medicine = Medicine.query.get_or_404(medicine_id)
        
        if not shopkeeper or medicine.shopkeeper_id != shopkeeper.id:
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        new_stock = data.get('stock_quantity')
        
        if new_stock is None:
            return jsonify({'error': 'stock_quantity is required'}), 400
        
        medicine.stock_quantity = int(new_stock)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Stock updated to {new_stock} units',
            'medicine': {
                'id': medicine.id,
                'name': medicine.name,
                'stock_quantity': medicine.stock_quantity
            }
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@api_bp.route('/inventory/low-stock', methods=['GET'])
def get_low_stock_items():
    """Get all low stock items for this shopkeeper"""
    if "shopkeeper" != 'shopkeeper':
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        shopkeeper = Shopkeeper.query.filter_by(user_id=1).first()
        if not shopkeeper:
            return jsonify({'error': 'Shopkeeper profile not found'}), 404
        
        # Get items with stock < 10
        low_stock_items = Medicine.query.filter(
            Medicine.shopkeeper_id == shopkeeper.id,
            Medicine.stock_quantity < 10
        ).all()
        
        items = [
            {
                'id': m.id,
                'name': m.name,
                'category': m.category,
                'current_stock': m.stock_quantity,
                'urgency': 'critical' if m.stock_quantity < 5 else 'warning'
            }
            for m in low_stock_items
        ]
        
        return jsonify({
            'success': True,
            'count': len(items),
            'low_stock_items': items
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/inventory/stats', methods=['GET'])
def get_inventory_stats():
    """Get inventory statistics"""
    if "shopkeeper" != 'shopkeeper':
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        from sqlalchemy import func
        
        shopkeeper = Shopkeeper.query.filter_by(user_id=1).first()
        if not shopkeeper:
            return jsonify({'error': 'Shopkeeper profile not found'}), 404
        
        medicines = Medicine.query.filter_by(shopkeeper_id=shopkeeper.id).all()
        
        # Calculate stats
        total_medicines = len(medicines)
        total_stock = sum(m.stock_quantity for m in medicines)
        low_stock_count = sum(1 for m in medicines if m.stock_quantity < 10)
        critical_stock_count = sum(1 for m in medicines if m.stock_quantity < 5)
        
        # Get total revenue from this shopkeeper's medicines
        total_revenue = db.session.query(func.sum(OrderItem.quantity * OrderItem.price_at_purchase)).join(
            Medicine
        ).filter(Medicine.shopkeeper_id == shopkeeper.id).scalar() or 0
        
        # Get top selling medicines
        top_medicines = db.session.query(
            Medicine.name,
            func.sum(OrderItem.quantity).label('total_sold')
        ).join(OrderItem).filter(
            Medicine.shopkeeper_id == shopkeeper.id
        ).group_by(Medicine.id).order_by(
            func.sum(OrderItem.quantity).desc()
        ).limit(5).all()
        
        top_items = [
            {'name': name, 'sold': int(sold) if sold else 0}
            for name, sold in top_medicines
        ]
        
        return jsonify({
            'success': True,
            'stats': {
                'total_medicines': total_medicines,
                'total_stock': total_stock,
                'low_stock_count': low_stock_count,
                'critical_stock_count': critical_stock_count,
                'total_revenue': float(total_revenue),
                'top_selling': top_items
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
