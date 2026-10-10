"""
Admin Portal Routes
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from functools import wraps
from app import db
from app.models import User, Shopkeeper, Medicine, Order, OrderItem, MedicineRating, DeliveryAgent, Delivery, DeliveryStatusUpdate, Doctor, DoctorAppointment, DoctorPrescription
from datetime import datetime
from urllib.parse import unquote
import requests
import random
import os

# Import medicine API
try:
    from app.rxnorm_api import MedicineAPI, format_medicine_data
except ImportError as e:
    print(f"Warning: MedicineAPI import failed: {e}")
    MedicineAPI = None
    format_medicine_data = None

# Custom decorator for admin-only routes (prevents redirect loops)
from app.models import Notification
def admin_required(f):
    """Decorator to require admin authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        
        if not current_user.is_admin:
            flash('You must be logged in as an admin', 'danger')
            logout_user()  # Log out non-admin users
            return redirect(url_for('auth.login'))
        
        return f(*args, **kwargs)
    
    return decorated_function


def _generate_delivery_otp():
    return f"{random.randint(0, 999999):06d}"


def _format_phone_for_sms(raw_phone):
    phone = (raw_phone or '').strip()
    if not phone:
        return None

    if phone.startswith('+'):
        digits = ''.join(ch for ch in phone if ch.isdigit())
        return f'+{digits}' if digits else None

    digits = ''.join(ch for ch in phone if ch.isdigit())
    if not digits:
        return None

    country_code = (current_app.config.get('SMS_COUNTRY_CODE') or '+91').strip()
    cc_digits = ''.join(ch for ch in country_code if ch.isdigit())
    if cc_digits and digits.startswith(cc_digits):
        return f'+{digits}'
    if cc_digits:
        return f'+{cc_digits}{digits}'
    return f'+{digits}'


def _send_sms_via_twilio(to_number, message):
    sid = (current_app.config.get('TWILIO_ACCOUNT_SID') or '').strip()
    token = (current_app.config.get('TWILIO_AUTH_TOKEN') or '').strip()
    from_number = (current_app.config.get('TWILIO_FROM_NUMBER') or '').strip()
    if not sid or not token or not from_number:
        return False, 'Missing Twilio configuration'

    url = f'https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json'
    try:
        response = requests.post(
            url,
            data={'To': to_number, 'From': from_number, 'Body': message},
            auth=(sid, token),
            timeout=10
        )
    except Exception as exc:
        return False, f'SMS request failed: {exc}'

    if 200 <= response.status_code < 300:
        return True, 'SMS sent'
    return False, f'Twilio error {response.status_code}'


def _send_delivery_otp_sms(order, otp_code):
    if not order or not order.user:
        return False, 'Customer details missing'

    to_number = _format_phone_for_sms(order.user.phone)
    if not to_number:
        return False, 'Customer phone number missing or invalid'

    message = (
        f'AcuMeds OTP for order #{order.id}: {otp_code}. '
        'Share this OTP with your delivery agent to complete delivery.'
    )

    provider = (current_app.config.get('SMS_PROVIDER') or 'console').strip().lower()
    if provider == 'twilio':
        return _send_sms_via_twilio(to_number, message)

    current_app.logger.info(
        'SMS fallback provider=%s, order_id=%s, to=%s, message=%s',
        provider,
        order.id,
        to_number,
        message
    )
    return False, 'Live SMS provider is not configured'


DELIVERY_FEE_DEFAULT = 30.0

# ==================== AUTH BLUEPRINT ====================
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login"""
    if current_user.is_authenticated and current_user.is_admin:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        remember_me = request.form.get('remember_me')
        
        # Try to find user by username or email
        user = None
        if username:
            user = User.query.filter_by(username=username).first()
            if not user:  # Also try as email
                user = User.query.filter_by(email=username).first()
        
        if user and user.check_password(password):
            if hasattr(user, 'is_active') and not user.is_active:
                flash('Your account has been deactivated.', 'danger')
                return redirect(url_for('auth.login'))
            if not user.is_admin:
                flash('Only admins can access this portal', 'danger')
                return redirect(url_for('auth.login'))
            
            login_user(user, remember=remember_me)
            flash(f'Welcome, {user.full_name or user.username}!', 'success')
            return redirect(url_for('dashboard.index'))
        
        flash('Invalid username/email or password', 'danger')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Admin logout"""
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('auth.login'))

# ==================== DASHBOARD BLUEPRINT ====================
dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@admin_required
def index():
    
    total_shopkeepers = Shopkeeper.query.count()
    verified_shopkeepers = Shopkeeper.query.filter_by(verified=True).count()
    pending_shopkeepers = Shopkeeper.query.filter_by(verified=False).count()
    
    total_medicines = Medicine.query.count()
    total_orders = Order.query.count()
    total_users = User.query.count()
    total_revenue = db.session.query(db.func.sum(Order.total_amount)).scalar() or 0
    
    recent_orders = Order.query.order_by(Order.order_date.desc()).limit(10).all()
    pending_shops = Shopkeeper.query.filter_by(verified=False).all()
    
    return render_template('dashboard/index.html',
                         total_shopkeepers=total_shopkeepers,
                         verified_shopkeepers=verified_shopkeepers,
                         pending_shopkeepers=pending_shopkeepers,
                         total_medicines=total_medicines,
                         total_orders=total_orders,
                         total_users=total_users,
                         total_revenue=total_revenue,
                         recent_orders=recent_orders,
                         pending_shops=pending_shops)

# ==================== SHOPKEEPER MANAGEMENT ====================
@dashboard_bp.route('/shopkeepers')
@admin_required
def shopkeepers():
    """Manage all shopkeepers"""
    shopkeepers = db.session.query(Shopkeeper).join(User).all()
    pending = [s for s in shopkeepers if (not s.verified and not s.verification_notes)]
    verified = [s for s in shopkeepers if s.verified]
    rejected = [s for s in shopkeepers if (not s.verified and s.verification_notes)]
    
    return render_template('dashboard/shopkeepers.html',
                         pending_count=len(pending),
                         verified_count=len(verified),
                         rejected_count=len(rejected),
                         pending_shopkeepers=pending,
                         verified_shopkeepers=verified,
                         rejected_shopkeepers=rejected)

@dashboard_bp.route('/shopkeeper/<int:shopkeeper_id>/verify', methods=['POST'])
@admin_required
def verify_shopkeeper(shopkeeper_id):
    """Verify a shopkeeper"""
    shopkeeper = Shopkeeper.query.get_or_404(shopkeeper_id)
    shopkeeper.verified = True
    db.session.commit()
    
    flash(f'✅ Shopkeeper "{shopkeeper.shop_name}" verified!', 'success')
    return redirect(url_for('dashboard.shopkeepers'))

@dashboard_bp.route('/shopkeeper/<int:shopkeeper_id>/reject', methods=['POST'])
@admin_required
def reject_shopkeeper(shopkeeper_id):
    """Reject a shopkeeper"""
    
    shopkeeper = Shopkeeper.query.get_or_404(shopkeeper_id)
    shop_name = shopkeeper.shop_name
    user_id = shopkeeper.user_id
    
    db.session.delete(shopkeeper)
    user = User.query.get(user_id)
    if user and user.role == 'shopkeeper':
        db.session.delete(user)
    
    db.session.commit()
    flash(f'❌ Shopkeeper "{shop_name}" rejected', 'info')
    return redirect(url_for('dashboard.shopkeepers'))

@dashboard_bp.route('/shopkeeper/<int:shopkeeper_id>/remove', methods=['POST'])
@admin_required
def remove_shopkeeper(shopkeeper_id):
    """Remove a verified shopkeeper and notify them"""
    shopkeeper = Shopkeeper.query.get_or_404(shopkeeper_id)
    reason = (request.form.get('reason') or '').strip()
    permanent_delete = request.form.get('permanent_delete') == 'on'
    if not reason:
        reason = 'Removed by admin.'

    if permanent_delete:
        shop_name = shopkeeper.shop_name
        user = User.query.get(shopkeeper.user_id)
        if user:
            db.session.delete(user)
        else:
            db.session.delete(shopkeeper)
        db.session.commit()
        current_app.logger.info(
            'Shopkeeper removed permanently: %s (reason: %s)',
            shop_name,
            reason
        )
        flash(f'Shopkeeper "{shop_name}" permanently deleted.', 'info')
        return redirect(url_for('dashboard.shopkeepers'))

    shopkeeper.verified = False
    shopkeeper.verified_at = None
    shopkeeper.verification_notes = reason

    notification = Notification(
        user_id=shopkeeper.user_id,
        title='Shopkeeper Access Removed',
        message=(
            f'Your shop "{shopkeeper.shop_name}" has been removed from the platform. '
            f'Reason: {reason}'
        ),
        notification_type='shopkeeper_removed'
    )
    db.session.add(notification)
    db.session.commit()

    flash(f'Shopkeeper "{shopkeeper.shop_name}" removed and notified.', 'info')
    return redirect(url_for('dashboard.shopkeepers'))


@dashboard_bp.route('/shopkeeper/<int:shopkeeper_id>/delete', methods=['POST'])
@admin_required
def delete_shopkeeper(shopkeeper_id):
    """Permanently delete a shopkeeper account"""
    shopkeeper = Shopkeeper.query.get_or_404(shopkeeper_id)
    shop_name = shopkeeper.shop_name
    user = User.query.get(shopkeeper.user_id)
    if user:
        db.session.delete(user)
    else:
        db.session.delete(shopkeeper)
    db.session.commit()
    flash(f'Shopkeeper "{shop_name}" permanently deleted.', 'info')
    return redirect(url_for('dashboard.shopkeepers'))


# ==================== DELIVERY MANAGEMENT ====================
@dashboard_bp.route('/delivery-agents')
@admin_required
def delivery_agents():
    agents = DeliveryAgent.query.order_by(DeliveryAgent.created_at.desc()).all()
    pending_agents = [agent for agent in agents if not agent.active]
    active_agents = [agent for agent in agents if agent.active]

    return render_template(
        'dashboard/delivery_agents.html',
        pending_agents=pending_agents,
        active_agents=active_agents,
        pending_count=len(pending_agents),
        active_count=len(active_agents)
    )


@dashboard_bp.route('/delivery-agents/<int:agent_id>/approve', methods=['POST'])
@admin_required
def approve_delivery_agent(agent_id):
    agent = DeliveryAgent.query.get_or_404(agent_id)
    agent.active = True
    if agent.user:
        agent.user.role = 'delivery'
    db.session.commit()
    flash('Delivery agent approved.', 'success')
    return redirect(url_for('dashboard.delivery_agents'))


@dashboard_bp.route('/delivery-agents/<int:agent_id>/deactivate', methods=['POST'])
@admin_required
def deactivate_delivery_agent(agent_id):
    agent = DeliveryAgent.query.get_or_404(agent_id)
    agent.active = False
    db.session.commit()
    flash('Delivery agent deactivated.', 'info')
    return redirect(url_for('dashboard.delivery_agents'))
# ==================== MEDICINES MANAGEMENT ====================
@dashboard_bp.route('/medicines')
@admin_required
def medicines():
    """Manage all medicines"""
    
    medicines = Medicine.query.all()
    return render_template('dashboard/medicines.html', medicines=medicines)

@dashboard_bp.route('/medicine/<int:med_id>/delete', methods=['POST'])
@admin_required
def delete_medicine(med_id):
    """Delete a medicine"""
    
    medicine = Medicine.query.get_or_404(med_id)
    med_name = medicine.name
    db.session.delete(medicine)
    db.session.commit()
    
    flash(f'Medicine "{med_name}" deleted', 'info')
    return redirect(url_for('dashboard.medicines'))

# ==================== ORDERS MANAGEMENT ====================
@dashboard_bp.route('/orders')
@admin_required
def orders():
    """Manage all orders"""

    orders = Order.query.order_by(Order.order_date.desc()).all()
    for order in orders:
        order.items = list(order.order_items or [])

    delivery_agents = DeliveryAgent.query.filter_by(active=True).order_by(DeliveryAgent.created_at.desc()).all()
    total_orders = len(orders)
    pending_orders = Order.query.filter_by(status='Pending').count()
    refunded_orders = Order.query.filter_by(refund_status='Refunded').count()
    refund_requests = Order.query.filter_by(refund_request_status='Requested').count()

    return render_template(
        'dashboard/orders.html',
        orders=orders,
        total_orders=total_orders,
        pending_orders=pending_orders,
        refunded_orders=refunded_orders,
        refund_requests=refund_requests,
        delivery_agents=delivery_agents
    )


@dashboard_bp.route('/order/<int:order_id>/delivery', methods=['POST'])
@admin_required
def assign_delivery(order_id):
    agent_id = request.form.get('delivery_agent_id')
    if not agent_id:
        flash('Please select a delivery agent.', 'warning')
        return redirect(url_for('dashboard.orders'))

    order = Order.query.get_or_404(order_id)
    agent = DeliveryAgent.query.get_or_404(int(agent_id))

    if not agent.active:
        flash('Selected delivery agent is inactive.', 'warning')
        return redirect(url_for('dashboard.orders'))

    delivery = Delivery.query.filter_by(order_id=order.id).first()
    if not delivery:
        delivery = Delivery(
            order_id=order.id,
            delivery_agent_id=agent.id,
            status='Assigned',
            otp_code=_generate_delivery_otp(),
            delivery_fee=DELIVERY_FEE_DEFAULT
        )
        db.session.add(delivery)
        db.session.flush()
    else:
        delivery.delivery_agent_id = agent.id
        delivery.status = 'Assigned'
        if not delivery.otp_code:
            delivery.otp_code = _generate_delivery_otp()

    delivery.assigned_at = datetime.utcnow()
    delivery.picked_up_at = None
    delivery.out_for_delivery_at = None
    delivery.delivered_at = None
    delivery.otp_verified_at = None

    if order.payment_method == 'Cash on Delivery' and order.payment_status != 'Paid':
        delivery.cash_to_collect = float(order.total_amount)
    else:
        delivery.cash_to_collect = 0.0

    db.session.add(DeliveryStatusUpdate(delivery_id=delivery.id, status='Assigned', note='Assigned by admin'))
    db.session.commit()

    flash('Delivery agent assigned to order.', 'success')
    sms_sent, sms_reason = _send_delivery_otp_sms(order, delivery.otp_code)
    if sms_sent:
        flash('OTP sent to customer mobile number.', 'success')
    else:
        current_app.logger.warning('Delivery OTP SMS not sent for order %s: %s', order.id, sms_reason)
        flash('OTP SMS not sent. Customer can still share OTP from order details page.', 'warning')

    return redirect(url_for('dashboard.orders'))


@dashboard_bp.route('/order/<int:order_id>/refund', methods=['POST'])
@admin_required
def process_refund(order_id):
    """Process a refund for a paid order and record the refund details."""
    order = Order.query.get_or_404(order_id)

    if order.payment_status != 'Paid':
        flash('Refunds can only be processed for paid orders.', 'warning')
        return redirect(url_for('dashboard.orders'))

    if (order.refund_status or '').lower() == 'refunded':
        flash('This order has already been refunded.', 'info')
        return redirect(url_for('dashboard.orders'))

    requested_reason = (getattr(order, 'refund_request_reason', None) or '').strip()
    requested_amount = getattr(order, 'refund_request_amount', None)
    refund_reason = (request.form.get('refund_reason') or '').strip() or requested_reason
    refund_amount_raw = (request.form.get('refund_amount') or '').strip()

    if not refund_reason:
        flash('Please enter a refund reason.', 'warning')
        return redirect(url_for('dashboard.orders'))

    try:
        if refund_amount_raw:
            refund_amount = float(refund_amount_raw)
        elif requested_amount is not None:
            refund_amount = float(requested_amount)
        else:
            refund_amount = float(order.total_amount)
    except (TypeError, ValueError):
        flash('Please enter a valid refund amount.', 'warning')
        return redirect(url_for('dashboard.orders'))

    if refund_amount <= 0:
        flash('Refund amount must be greater than zero.', 'warning')
        return redirect(url_for('dashboard.orders'))

    if refund_amount > float(order.total_amount):
        flash('Refund amount cannot exceed the order total.', 'warning')
        return redirect(url_for('dashboard.orders'))

    admin_name = (getattr(current_user, 'full_name', None) or getattr(current_user, 'username', None) or 'Admin').strip()

    order.payment_status = 'Refunded'
    if order.status not in ('Delivered', 'Cancelled'):
        order.status = 'Cancelled'
    order.refund_request_status = 'Processed'
    order.refund_status = 'Refunded'
    order.refund_amount = round(refund_amount, 2)
    order.refund_reason = refund_reason
    order.refund_processed_at = datetime.utcnow()
    order.refund_processed_by = admin_name

    if order.delivery:
        order.delivery.cash_to_collect = 0.0

    notification = Notification(
        user_id=order.user_id,
        title=f'Refund processed for order #{order.id}',
        message=(
            f'Your refund of ₹{order.refund_amount:.2f} for order #{order.id} has been processed. '
            f'Reason: {refund_reason}'
        ),
        notification_type='refund_processed'
    )
    db.session.add(notification)
    db.session.commit()

    flash(f'Refund processed for order #{order.id}.', 'success')
    return redirect(url_for('dashboard.orders'))


@dashboard_bp.route('/ratings')
@admin_required
def ratings():
    """View all customer ratings"""
    ratings = MedicineRating.query.order_by(MedicineRating.created_at.desc()).all()
    avg_rating = db.session.query(db.func.avg(MedicineRating.rating)).scalar() or 0
    return render_template('dashboard/ratings.html',
                           ratings=ratings,
                           total_ratings=len(ratings),
                           avg_rating=round(avg_rating, 2))

@dashboard_bp.route('/order/<int:order_id>/status', methods=['POST'])
@admin_required
def update_order_status(order_id):
    """Order status updates are handled by shopkeepers"""
    message = 'Order status updates are managed by shopkeepers.'

    if request.is_json:
        return jsonify({'success': False, 'error': message}), 403

    flash(message, 'warning')
    return redirect(url_for('dashboard.orders'))

# ==================== USERS MANAGEMENT ====================
@dashboard_bp.route('/users')
@admin_required
def users():
    """Manage all users"""

    users_list = User.query.order_by(User.created_at.desc()).all()
    customers = [u for u in users_list if (not u.role or u.role == 'customer') and not u.is_admin]
    admins = [u for u in users_list if u.is_admin or u.role == 'admin']

    # Get shopkeeper objects, not User objects filtered by role
    shopkeepers = Shopkeeper.query.all()

    return render_template('dashboard/users.html',
                         users=users_list,
                         customers=customers,
                         shopkeepers=shopkeepers,
                         admins=admins,
                         total_users=len(users_list),
                         customer_count=len(customers),
                         shopkeeper_count=len(shopkeepers))


@dashboard_bp.route('/users/<int:user_id>/toggle-active', methods=['POST'])
@admin_required
def toggle_user_active(user_id):
    """Activate or deactivate a customer account"""
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot deactivate your own account.', 'warning')
        return redirect(url_for('dashboard.users'))
    if user.is_admin or user.role == 'admin':
        flash('Admin accounts cannot be deactivated here.', 'warning')
        return redirect(url_for('dashboard.users'))
    if user.role == 'shopkeeper' or user.shopkeeper:
        flash('Use the Shopkeepers page to manage shopkeeper access.', 'info')
        return redirect(url_for('dashboard.users'))

    user.is_active = not bool(getattr(user, 'is_active', True))
    db.session.commit()
    status_label = 'activated' if user.is_active else 'deactivated'
    flash(f'User "{user.username}" {status_label}.', 'success')
    return redirect(url_for('dashboard.users'))


@dashboard_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    """Permanently delete a customer account"""
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'warning')
        return redirect(url_for('dashboard.users'))
    if user.is_admin or user.role == 'admin':
        flash('Admin accounts cannot be deleted here.', 'warning')
        return redirect(url_for('dashboard.users'))
    if user.role == 'shopkeeper' or user.shopkeeper:
        flash('Use the Shopkeepers page to remove shopkeepers.', 'info')
        return redirect(url_for('dashboard.users'))

    username = user.username
    db.session.delete(user)
    db.session.commit()
    flash(f'User "{username}" permanently deleted.', 'info')
    return redirect(url_for('dashboard.users'))

# ==================== ANALYTICS ====================
@dashboard_bp.route('/analytics')
@admin_required
def analytics():
    """View analytics"""
    
    # Basic counts
    total_shopkeepers = Shopkeeper.query.count()
    verified_shopkeepers = Shopkeeper.query.filter_by(verified=True).count()
    pending_shopkeepers = Shopkeeper.query.filter_by(verified=False).count()
    
    total_medicines = Medicine.query.count()
    total_orders = Order.query.count()
    total_users = User.query.count()
    
    # Revenue calculations
    total_revenue = db.session.query(db.func.sum(Order.total_amount)).scalar() or 0
    
    # This month's revenue
    current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_revenue = db.session.query(db.func.sum(Order.total_amount)).filter(
        Order.order_date >= current_month_start
    ).scalar() or 0
    
    # Orders this month
    orders_this_month = Order.query.filter(Order.order_date >= current_month_start).count()
    
    # Average order value
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
    
    # Order status breakdown (case-insensitive)
    status_rows = db.session.query(
        db.func.lower(Order.status).label('status'),
        db.func.count(Order.id)
    ).group_by(db.func.lower(Order.status)).all()
    status_counts = {
        ((status or '').strip().lower()): count for status, count in status_rows
    }

    delivered_count = status_counts.get('delivered', 0)
    shipped_count = status_counts.get('shipped', 0)
    processing_count = sum(status_counts.get(key, 0) for key in ('processing', 'confirmed', 'ready'))
    pending_count = status_counts.get('pending', 0)
    cancelled_count = status_counts.get('cancelled', 0)
    
    # Calculate percentages
    if total_orders > 0:
        delivered_percent = (delivered_count / total_orders) * 100
        shipped_percent = (shipped_count / total_orders) * 100
        processing_percent = (processing_count / total_orders) * 100
        pending_percent = (pending_count / total_orders) * 100
        cancelled_percent = (cancelled_count / total_orders) * 100
        fulfillment_rate = ((delivered_count + shipped_count) / total_orders) * 100
    else:
        delivered_percent = shipped_percent = processing_percent = pending_percent = cancelled_percent = 0
        fulfillment_rate = 0
    
    # Active users (simplified: count of users)
    active_users = User.query.count()
    
    # Low stock items (< 20 units)
    low_stock_count = Medicine.query.filter(Medicine.stock_quantity < 20).count()
    
    # Database size (from active SQLAlchemy URI)
    db_size = 0
    database_uri = current_app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if database_uri.startswith('sqlite:///'):
        db_path = unquote(database_uri[len('sqlite:///'):])
        if os.name == 'nt' and db_path.startswith('/'):
            db_path = db_path.lstrip('/')
        db_path = os.path.abspath(db_path)
        if os.path.exists(db_path):
            db_size = round(os.path.getsize(db_path) / (1024 * 1024), 2)  # Convert to MB
    
    # Top shopkeepers (with medicine and order counts)
    top_shopkeepers = Shopkeeper.query.all()
    for shop in top_shopkeepers:
        shop.order_count = Order.query.join(
            OrderItem, Order.id == OrderItem.order_id
        ).join(
            Medicine, OrderItem.medicine_id == Medicine.id
        ).filter(Medicine.shopkeeper_id == shop.id).count()
    
    top_shopkeepers = sorted(top_shopkeepers, key=lambda x: x.order_count, reverse=True)
    
    # Top medicines (with sales count)
    top_medicines = Medicine.query.all()
    for med in top_medicines:
        med.sales_count = db.session.query(db.func.sum(OrderItem.quantity)).filter(
            OrderItem.medicine_id == med.id
        ).scalar() or 0
    
    top_medicines = sorted(top_medicines, key=lambda x: x.sales_count, reverse=True)
    
    # Shopkeeper statistics for table
    shopkeeper_stats = Shopkeeper.query.all()
    for shop in shopkeeper_stats:
        # Count orders for this shopkeeper's medicines
        shop.order_count = Order.query.join(
            OrderItem, Order.id == OrderItem.order_id
        ).join(
            Medicine, OrderItem.medicine_id == Medicine.id
        ).filter(Medicine.shopkeeper_id == shop.id).count()
        
        # Calculate revenue for this shopkeeper
        shop.total_revenue = db.session.query(db.func.sum(OrderItem.quantity * Medicine.price)).join(
            Medicine, OrderItem.medicine_id == Medicine.id
        ).filter(Medicine.shopkeeper_id == shop.id).scalar() or 0
        
        shop.avg_rating = 'N/A'  # Can be enhanced with reviews in future
    
    return render_template('dashboard/analytics.html',
                         total_shopkeepers=total_shopkeepers,
                         verified_shopkeepers=verified_shopkeepers,
                         pending=pending_shopkeepers,
                         total_medicines=total_medicines,
                         total_orders=total_orders,
                         total_users=total_users,
                         total_revenue=total_revenue,
                         monthly_revenue=monthly_revenue,
                         orders_this_month=orders_this_month,
                         avg_order_value=avg_order_value,
                         fulfillment_rate=fulfillment_rate,
                         delivered_count=delivered_count,
                         shipped_count=shipped_count,
                         processing_count=processing_count,
                         pending_count=pending_count,
                         cancelled_count=cancelled_count,
                         delivered_percent=delivered_percent,
                         shipped_percent=shipped_percent,
                         processing_percent=processing_percent,
                         pending_percent=pending_percent,
                         cancelled_percent=cancelled_percent,
                         active_users=active_users,
                         low_stock_count=low_stock_count,
                         db_size=db_size,
                         top_shopkeepers=top_shopkeepers,
                         top_medicines=top_medicines,
                         shopkeeper_stats=shopkeeper_stats)


@dashboard_bp.route('/medicine-importer')
@admin_required
def medicine_importer():
    """Open medicine database importer"""
    
    shopkeepers = Shopkeeper.query.filter_by(verified=True).all()
    return render_template('dashboard/medicine_importer.html', shopkeepers=shopkeepers)


# ==================== MEDICINE API BLUEPRINT ====================
api_bp = Blueprint('medicine_api', __name__, url_prefix='/api/medicines')

@api_bp.route('/search', methods=['GET'])
@admin_required
def search_medicines_api():
    """
    Search medicines from the free medicine database
    Query params: q=medicine_name
    """
    
    if not MedicineAPI:
        return jsonify({'error': 'Medicine API not available'}), 500
    
    search_term = request.args.get('q', '').strip()
    if not search_term or len(search_term) < 2:
        return jsonify({'error': 'Search term must be at least 2 characters'}), 400
    
    try:
        results = MedicineAPI.search_medicines(search_term)
        return jsonify({
            'success': True,
            'count': len(results),
            'medicines': results
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/categories', methods=['GET'])
@admin_required
def get_categories_api():
    """Get all medicine categories"""
    
    if not MedicineAPI:
        return jsonify({'error': 'Medicine API not available'}), 500
    
    try:
        categories = MedicineAPI.get_all_categories()
        return jsonify({
            'success': True,
            'categories': categories
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/condition-search', methods=['GET'])
@admin_required
def search_by_condition_api():
    """
    Search medicines for a specific medical condition
    Query params: condition=fever
    """
    
    if not MedicineAPI:
        return jsonify({'error': 'Medicine API not available'}), 500
    
    condition = request.args.get('condition', '').strip()
    if not condition:
        return jsonify({'error': 'Condition parameter required'}), 400
    
    try:
        results = MedicineAPI.search_by_condition(condition)
        return jsonify({
            'success': True,
            'condition': condition,
            'count': len(results),
            'medicines': results
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/import', methods=['POST'])
@admin_required
def import_medicine_api():
    """
    Import a medicine from the database into the pharmacy system
    POST data: medicine_id, price (optional), shopkeeper_id (optional)
    """
    
    if not MedicineAPI:
        return jsonify({'error': 'Medicine API not available'}), 500
    
    data = request.get_json() or {}
    medicine_id = data.get('medicine_id', '').strip()
    custom_price = data.get('price')
    shopkeeper_id = data.get('shopkeeper_id')
    
    if not medicine_id:
        return jsonify({'error': 'medicine_id is required'}), 400
    
    try:
        # Get medicine info from the medicine database
        med_info = MedicineAPI.get_medicine_info(medicine_id)
        if not med_info:
            return jsonify({'error': f'Medicine "{medicine_id}" not found in database'}), 404
        
        # Format for pharmacy system
        med_data = format_medicine_data(med_info, custom_price or med_info.get('price', 0))
        
        # Check if medicine already exists
        existing = Medicine.query.filter_by(name=med_data['name']).first()
        if existing:
            return jsonify({
                'error': f'Medicine "{med_data["name"]}" already exists',
                'existing_id': existing.id
            }), 409
        
        # Create new medicine
        new_medicine = Medicine(
            name=med_data['name'],
            category=med_data['category'],
            description=med_data['description'],
            price=med_data['price'],
            stock_quantity=med_data['stock_quantity'],
            requires_prescription=med_data['requires_prescription'],
            side_effects=med_data['side_effects'],
            usage_instructions=med_data['usage_instructions'],
            image=med_data['image'],
            shopkeeper_id=shopkeeper_id  # Can be None for system-wide medicines
        )
        
        db.session.add(new_medicine)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Medicine "{new_medicine.name}" imported successfully',
            'medicine_id': new_medicine.id,
            'medicine': {
                'id': new_medicine.id,
                'name': new_medicine.name,
                'category': new_medicine.category,
                'price': new_medicine.price
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@api_bp.route('/all', methods=['GET'])
@admin_required
def get_all_medicines_api():
    """Get all medicines from the database"""
    
    if not MedicineAPI:
        return jsonify({'error': 'Medicine API not available'}), 500
    
    try:
        medicines = MedicineAPI.get_all_medicines()
        return jsonify({
            'success': True,
            'count': len(medicines),
            'medicines': medicines
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== ANALYTICS API ====================
@api_bp.route('/analytics', methods=['GET'])
@admin_required
def get_analytics_data():
    """Get analytics data for the dashboard"""
    
    try:
        from sqlalchemy import func
        from datetime import timedelta
        
        # Basic counts
        total_orders = Order.query.count()
        total_users = User.query.count()
        total_medicines = Medicine.query.count()
        total_shopkeepers = Shopkeeper.query.count()
        
        # Total revenue
        total_revenue = db.session.query(func.sum(Order.total_amount)).scalar() or 0
        
        # Get last 30 days revenue (monthly trend)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        monthly_revenue = db.session.query(func.sum(Order.total_amount)).filter(
            Order.order_date >= thirty_days_ago
        ).scalar() or 0
        
        # Orders by status
        orders_by_status = db.session.query(
            Order.status,
            func.count(Order.id).label('count')
        ).group_by(Order.status).all()
        
        status_data = {status: count for status, count in orders_by_status}
        
        # Top 5 selling medicines
        top_medicines = db.session.query(
            Medicine.name,
            func.sum(OrderItem.quantity).label('total_sold'),
            func.sum(OrderItem.quantity * OrderItem.price_at_purchase).label('revenue')
        ).join(OrderItem).group_by(Medicine.id).order_by(
            func.sum(OrderItem.quantity).desc()
        ).limit(5).all()
        
        top_medicines_data = [
            {
                'name': med[0],
                'total_sold': int(med[1]) if med[1] else 0,
                'revenue': float(med[2]) if med[2] else 0
            }
            for med in top_medicines
        ]
        
        # Monthly revenue trend (last 12 months)
        monthly_trend = []
        for i in range(11, -1, -1):
            month_start = datetime.utcnow() - timedelta(days=30*i)
            month_end = datetime.utcnow() - timedelta(days=30*(i-1))
            month_revenue = db.session.query(func.sum(Order.total_amount)).filter(
                Order.order_date.between(month_start, month_end)
            ).scalar() or 0
            monthly_trend.append({
                'month': month_start.strftime('%b'),
                'revenue': float(month_revenue)
            })
        
        # Active users (users who placed orders in last 30 days)
        active_users = db.session.query(func.count(func.distinct(Order.user_id))).filter(
            Order.order_date >= thirty_days_ago
        ).scalar() or 0
        
        return jsonify({
            'success': True,
            'summary': {
                'total_orders': total_orders,
                'total_users': total_users,
                'total_medicines': total_medicines,
                'total_shopkeepers': total_shopkeepers,
                'total_revenue': float(total_revenue),
                'monthly_revenue': float(monthly_revenue),
                'active_users_30d': int(active_users)
            },
            'orders_by_status': status_data,
            'top_medicines': top_medicines_data,
            'monthly_trend': monthly_trend
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# ==================== DOCTOR MANAGEMENT ROUTES ====================
@dashboard_bp.route('/doctors')
@admin_required
def manage_doctors():
    """View and manage doctor registrations and verification status"""
    doctors = Doctor.query.order_by(Doctor.created_at.desc()).all()
    pending = [d for d in doctors if not d.is_verified]
    approved = [d for d in doctors if d.is_verified]
    total_appointments = DoctorAppointment.query.count()

    return render_template(
        'dashboard/doctors.html',
        doctors=doctors,
        pending_doctors=pending,
        approved_doctors=approved,
        total_appointments=total_appointments
    )


@dashboard_bp.route('/doctor/<int:doctor_id>/verify', methods=['POST'])
@admin_required
def verify_doctor(doctor_id):
    """Approve/Verify doctor license and generate official Confirmation & Authorization Letter"""
    import uuid
    doctor = Doctor.query.get_or_404(doctor_id)
    notes = request.form.get('verification_notes', '').strip()
    
    # Generate official approval letter reference
    appr_ref = f"ACU-DOC-APPR-{datetime.utcnow().strftime('%Y%m')}-{uuid.uuid4().hex[:6].upper()}"
    
    doctor.is_verified = True
    doctor.is_available = True
    doctor.verified_at = datetime.utcnow()
    doctor.approval_letter_ref = appr_ref
    doctor.verification_notes = notes or 'Medical license verified and approved by AcuMeds Admin Medical Board.'
    doctor.rejection_reason = None
    
    # Create congratulatory notification for the doctor
    notif = Notification(
        user_id=doctor.user_id,
        title='Doctor Registration Approved & Verified! 🎉',
        message=f'Your doctor registration has been approved by the Admin Medical Board. Authorization Ref: {appr_ref}. You now have full access to patient consultations and prescriptions.',
        notification_type='doctor_approval'
    )
    db.session.add(notif)
    db.session.commit()
    
    flash(f'Dr. {doctor.user.full_name or doctor.user.username} approved successfully! Confirmation letter issued (Ref: {appr_ref}).', 'success')
    return redirect(url_for('dashboard.manage_doctors'))


@dashboard_bp.route('/doctor/<int:doctor_id>/reject', methods=['POST'])
@admin_required
def reject_doctor(doctor_id):
    """Reject doctor registration or request re-verification with notes"""
    doctor = Doctor.query.get_or_404(doctor_id)
    reason = request.form.get('rejection_reason', 'Medical council license details could not be validated. Please update your registration documents.').strip()
    
    doctor.is_verified = False
    doctor.is_available = False
    doctor.rejection_reason = reason
    
    # Send notification to doctor
    notif = Notification(
        user_id=doctor.user_id,
        title='Doctor Registration Update Required',
        message=f'Your registration application could not be approved at this time: {reason}',
        notification_type='doctor_rejection'
    )
    db.session.add(notif)
    db.session.commit()
    
    flash(f'Dr. {doctor.user.full_name or doctor.user.username} application marked for revision.', 'warning')
    return redirect(url_for('dashboard.manage_doctors'))


@dashboard_bp.route('/doctor/<int:doctor_id>/letter')
@admin_required
def doctor_letter(doctor_id):
    """View official Confirmation / Approval Letter from Admin Portal"""
    doctor = Doctor.query.get_or_404(doctor_id)
    return render_template('dashboard/doctor_letter.html', doctor=doctor)


@dashboard_bp.route('/doctor/<int:doctor_id>/toggle', methods=['POST'])
@admin_required
def toggle_doctor_availability(doctor_id):
    """Toggle doctor availability status"""
    doctor = Doctor.query.get_or_404(doctor_id)
    doctor.is_available = not doctor.is_available
    db.session.commit()
    flash(f'Doctor availability updated.', 'info')
    return redirect(url_for('dashboard.manage_doctors'))


@dashboard_bp.route('/doctor-appointments')
@admin_required
def doctor_appointments_admin():
    """View all platform-wide doctor appointments"""
    appointments = DoctorAppointment.query.order_by(DoctorAppointment.id.desc()).all()
    return render_template('dashboard/doctor_appointments.html', appointments=appointments)



