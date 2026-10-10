"""
Unified Order Management System
Handles orders for customers, shopkeepers, and admins in one integrated view
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import Order, OrderItem, Notification, Medicine, Shopkeeper, User
from datetime import datetime, timedelta
from functools import wraps

unified_bp = Blueprint('unified_orders', __name__, url_prefix='/orders')

def require_admin(f):
    """Decorator to require admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def send_notification(user_id, title, message, notification_type, order_id=None):
    """Send notification to a user"""
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        notification_type=notification_type,
        related_order_id=order_id
    )
    db.session.add(notification)
    db.session.commit()

# ===========================
# CUSTOMER DASHBOARD
# ===========================

@unified_bp.route('/my-orders')
@login_required
def my_orders():
    """Customer - View their orders"""
    if current_user.role != 'customer':
        flash('Access denied', 'error')
        return redirect(url_for('main.dashboard'))
    
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    
    return render_template('orders/customer_orders.html', orders=orders)

@unified_bp.route('/order/<int:order_id>')
@login_required
def view_order(order_id):
    """View order details"""
    order = Order.query.get_or_404(order_id)
    
    # Check access - customer can only see their own orders, shopkeeper can see assigned orders, admin can see all
    if current_user.role == 'customer' and order.user_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('unified_orders.my_orders'))
    elif current_user.role == 'shopkeeper':
        if not current_user.shopkeeper or order.shopkeeper_id != current_user.shopkeeper.id:
            flash('Access denied', 'error')
            return redirect(url_for('shopkeeper_dashboard.dashboard'))
    
    return render_template('orders/order_detail.html', order=order)

# ===========================
# SHOPKEEPER DASHBOARD
# ===========================

@unified_bp.route('/shopkeeper-orders')
@login_required
def shopkeeper_orders():
    """Shopkeeper - View assigned and available orders"""
    if current_user.role != 'shopkeeper' or not current_user.shopkeeper:
        flash('Shopkeeper access required', 'error')
        return redirect(url_for('auth.login'))
    
    shopkeeper = current_user.shopkeeper
    
    # Orders assigned to this shopkeeper
    assigned_orders = Order.query.filter_by(shopkeeper_id=shopkeeper.id).order_by(Order.created_at.desc()).all()
    
    # Available orders (pending, not assigned)
    available_orders = Order.query.filter_by(shopkeeper_id=None, status='Pending').order_by(Order.created_at.desc()).all()
    
    return render_template('orders/shopkeeper_orders.html', 
                         assigned_orders=assigned_orders,
                         available_orders=available_orders)

@unified_bp.route('/accept-order/<int:order_id>', methods=['POST'])
@login_required
def accept_order(order_id):
    """Shopkeeper - Accept an available order"""
    if current_user.role != 'shopkeeper' or not current_user.shopkeeper:
        return jsonify({'success': False, 'error': 'Shopkeeper access required'}), 403
    
    order = Order.query.get_or_404(order_id)
    
    if order.shopkeeper_id is not None:
        return jsonify({'success': False, 'error': 'Order already assigned'}), 400
    
    # Assign order to shopkeeper
    order.shopkeeper_id = current_user.shopkeeper.id
    order.assigned_date = datetime.utcnow()
    order.status = 'Assigned'
    order.updated_at = datetime.utcnow()
    db.session.commit()
    
    # Notify customer
    send_notification(
        order.user_id,
        'Order Accepted',
        f'Your order #{order.id} has been accepted by {current_user.shopkeeper.shop_name}',
        'order_accepted',
        order.id
    )
    
    # Notify admin
    for admin in User.query.filter_by(is_admin=True).all():
        send_notification(
            admin.id,
            'Order Assigned',
            f'Order #{order.id} assigned to {current_user.shopkeeper.shop_name}',
            'order_assigned',
            order.id
        )
    
    return jsonify({'success': True, 'message': 'Order accepted successfully'})

@unified_bp.route('/update-order-status/<int:order_id>', methods=['POST'])
@login_required
def update_order_status(order_id):
    """Update order status - shopkeeper marks as ready, admin marks as delivered"""
    order = Order.query.get_or_404(order_id)
    
    # Shopkeeper can update to "Ready"
    if current_user.role == 'shopkeeper':
        if not current_user.shopkeeper or order.shopkeeper_id != current_user.shopkeeper.id:
            return jsonify({'success': False, 'error': 'Access denied'}), 403
        
        data = request.get_json()
        new_status = data.get('status')
        
        if new_status == 'Ready':
            order.status = 'Ready'
            order.updated_at = datetime.utcnow()
            db.session.commit()
            
            # Notify customer
            send_notification(
                order.user_id,
                'Order Ready for Pickup',
                f'Your order #{order.id} is ready for pickup at {current_user.shopkeeper.shop_name}',
                'order_ready',
                order.id
            )
            
            # Notify admin
            for admin in User.query.filter_by(is_admin=True).all():
                send_notification(
                    admin.id,
                    'Order Ready',
                    f'Order #{order.id} ready at {current_user.shopkeeper.shop_name}',
                    'order_ready',
                    order.id
                )
            
            return jsonify({'success': True, 'message': 'Order marked as ready'})
    
    # Admin can update to "Delivered"
    elif current_user.is_admin:
        data = request.get_json()
        new_status = data.get('status')
        
        if new_status == 'Delivered':
            order.status = 'Delivered'
            order.delivery_date = datetime.utcnow()
            order.updated_at = datetime.utcnow()
            db.session.commit()
            
            # Notify customer
            send_notification(
                order.user_id,
                'Order Delivered',
                f'Your order #{order.id} has been delivered',
                'order_delivered',
                order.id
            )
            
            # Notify shopkeeper
            if order.shopkeeper_id:
                send_notification(
                    order.shopkeeper.user_id,
                    'Order Delivered',
                    f'Order #{order.id} marked as delivered in system',
                    'order_delivered',
                    order.id
                )
            
            return jsonify({'success': True, 'message': 'Order marked as delivered'})
    
    return jsonify({'success': False, 'error': 'Invalid action'}), 400

# ===========================
# ADMIN DASHBOARD
# ===========================

@unified_bp.route('/admin-dashboard')
@login_required
@require_admin
def admin_dashboard():
    """Admin - View all orders and system statistics"""
    
    # Order statistics
    total_orders = Order.query.count()
    pending_orders = Order.query.filter_by(status='Pending').count()
    assigned_orders = Order.query.filter_by(status='Assigned').count()
    ready_orders = Order.query.filter_by(status='Ready').count()
    delivered_orders = Order.query.filter_by(status='Delivered').count()
    
    # Orders by shopkeeper
    orders_by_shopkeeper = db.session.query(Shopkeeper, Order).filter(
        Shopkeeper.id == Order.shopkeeper_id
    ).all()
    
    # All unread notifications for admins
    unread_notifications = Notification.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).order_by(Notification.created_at.desc()).limit(10).all()
    
    # Get all orders
    all_orders = Order.query.order_by(Order.created_at.desc()).limit(50).all()
    
    return render_template('orders/admin_dashboard.html',
                         total_orders=total_orders,
                         pending_orders=pending_orders,
                         assigned_orders=assigned_orders,
                         ready_orders=ready_orders,
                         delivered_orders=delivered_orders,
                         all_orders=all_orders,
                         unread_notifications=unread_notifications)

@unified_bp.route('/admin-orders')
@login_required
@require_admin
def admin_orders():
    """Admin - View all orders with detailed management options"""
    
    # Get filter parameters
    status_filter = request.args.get('status', 'all')
    shopkeeper_filter = request.args.get('shopkeeper_id', 'all')
    
    query = Order.query
    
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    if shopkeeper_filter != 'all':
        query = query.filter_by(shopkeeper_id=int(shopkeeper_filter))
    
    orders = query.order_by(Order.created_at.desc()).all()
    shopkeepers = Shopkeeper.query.all()
    
    return render_template('orders/admin_all_orders.html',
                         orders=orders,
                         shopkeepers=shopkeepers,
                         status_filter=status_filter,
                         shopkeeper_filter=shopkeeper_filter)

# ===========================
# NOTIFICATIONS
# ===========================

@unified_bp.route('/notifications')
@login_required
def get_notifications():
    """Get user's notifications"""
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(
        Notification.created_at.desc()
    ).limit(20).all()
    
    return render_template('orders/notifications.html', notifications=notifications)

@unified_bp.route('/notifications/mark-read/<int:notification_id>', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    """Mark notification as read"""
    notification = Notification.query.get_or_404(notification_id)
    
    if notification.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Access denied'}), 403
    
    notification.is_read = True
    db.session.commit()
    
    return jsonify({'success': True})

@unified_bp.route('/unread-count')
@login_required
def unread_count():
    """Get unread notification count"""
    count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    return jsonify({'unread_count': count})
