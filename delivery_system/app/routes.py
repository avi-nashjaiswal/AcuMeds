"""
Routes for Delivery App
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
from urllib.parse import quote_plus
import requests

from app import db
from app.models import User, DeliveryAgent, Order, Delivery, DeliveryStatusUpdate
from app.localization import get_language_label, set_current_language, translate as t

def _require_delivery_agent():
    if not current_user.is_authenticated or current_user.role != 'delivery':
        flash(t('messages.delivery_access_required'), 'danger')
        return None
    agent = DeliveryAgent.query.filter_by(user_id=current_user.id).first()
    if not agent or not agent.active:
        flash(t('messages.delivery_account_inactive'), 'warning')
        return None
    return agent


def _build_google_maps_url(order, delivery=None):
    """Return Google Maps search URL for order destination."""
    if order and order.delivery_address:
        destination = order.delivery_address.strip()
    elif order and order.user and order.user.address:
        destination = order.user.address.strip()
    else:
        destination = ''

    if destination:
        return f"https://www.google.com/maps/search/?api=1&query={quote_plus(destination)}"

    if delivery and delivery.last_lat is not None and delivery.last_lng is not None:
        return f"https://www.google.com/maps/search/?api=1&query={delivery.last_lat},{delivery.last_lng}"

    return None


def _build_google_maps_directions_url(order, delivery=None):
    """Return Google Maps directions URL to order destination."""
    if order and order.delivery_address:
        destination = order.delivery_address.strip()
    elif order and order.user and order.user.address:
        destination = order.user.address.strip()
    elif delivery and delivery.last_lat is not None and delivery.last_lng is not None:
        destination = f"{delivery.last_lat},{delivery.last_lng}"
    else:
        destination = ''

    if not destination:
        return None

    return f"https://www.google.com/maps/dir/?api=1&destination={quote_plus(destination)}&travelmode=driving"


# ==================== MAIN BLUEPRINT ====================

main_bp = Blueprint('main', __name__)


@main_bp.route('/language/<language_code>')
def set_language(language_code):
    chosen_language = set_current_language(language_code)
    flash(t('messages.language_changed', language=get_language_label(chosen_language)), 'success')
    next_url = request.args.get('next') or request.referrer or url_for('main.home')
    return redirect(next_url)


def _build_local_ai_answer(question, page):
    """Fallback helper when external AI service is unavailable."""
    question_text = (question or '').strip().lower()
    page_text = (page or '').strip().lower()

    if question_text in {'hi', 'hello', 'hey'} or question_text.startswith(('hi ', 'hello ', 'hey ')):
        return (
            'Hi! I can help with delivery dashboard actions, status updates, OTP verification, and payout tracking.'
        )

    if 'otp' in question_text or 'verify' in question_text:
        return (
            'Open delivery details, enter the customer OTP in the verification form, then submit to mark as delivered.'
        )

    if 'status' in question_text or 'picked' in question_text or 'out for delivery' in question_text:
        return (
            'Use the status form in delivery details and follow sequence: Picked Up, then Out for Delivery, then OTP verify.'
        )

    if 'location' in question_text or 'lat' in question_text or 'lng' in question_text:
        return 'Use the location update form on delivery details to push your latest latitude and longitude.'

    if 'earning' in question_text or 'cash' in question_text or 'dashboard' in page_text:
        return 'Delivery dashboard shows assigned orders, completed count, weekly earnings, and pending cash collection.'

    return (
        'AI is in basic help mode right now. '
        'Ask about delivery status, OTP verification, location updates, or earnings.'
    )


@main_bp.route('/ai-bot', methods=['POST'])
def ai_bot():
    """Return AI assistant response for delivery portal pages."""
    data = request.get_json(silent=True) or {}
    question = (data.get('question') or '').strip()
    page = (data.get('page') or '').strip()

    if not question:
        return jsonify({'answer': t('messages.enter_question')}), 400

    openai_api_key = (current_app.config.get('OPENAI_API_KEY') or '').strip()
    if not openai_api_key:
        return jsonify({'answer': _build_local_ai_answer(question, page)}), 200

    model_name = (current_app.config.get('OPENAI_MODEL') or 'gpt-4o-mini').strip() or 'gpt-4o-mini'
    prompt = (
        f'Portal: Delivery Agent\nPage: {page}\n'
        f'User question: {question}\n'
        'Answer in short practical steps for a delivery agent.'
    )

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
                    {'role': 'system', 'content': 'You are a helpful assistant for a medicine delivery portal.'},
                    {'role': 'user', 'content': prompt}
                ],
                'max_tokens': 220
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


@main_bp.route('/')
def home():
    if current_user.is_authenticated:
        if current_user.role == 'delivery':
            return redirect(url_for('delivery.delivery_dashboard'))
        logout_user()
        flash(t('messages.only_delivery_portal'), 'warning')
        return redirect(url_for('auth.login'))
    return render_template('auth/welcome.html')


# ==================== AUTH BLUEPRINT ====================

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login for delivery users"""
    if current_user.is_authenticated:
        if current_user.role == 'delivery':
            return redirect(url_for('delivery.delivery_dashboard'))
        logout_user()
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        identity = (request.form.get('identity') or '').strip()
        password = (request.form.get('password') or '').strip()

        user = User.query.filter_by(email=identity).first()
        if not user:
            user = User.query.filter_by(username=identity).first()
        if not user:
            user = User.query.filter_by(phone=identity).first()

        if user and user.check_password(password):
            if user.role != 'delivery':
                flash(t('messages.only_delivery_signin'), 'danger')
                return redirect(url_for('auth.login'))

            agent = DeliveryAgent.query.filter_by(user_id=user.id).first()
            if not agent or not agent.active:
                flash(t('messages.pending_approval'), 'warning')
                return redirect(url_for('auth.login'))

            login_user(user, remember=True)
            return redirect(url_for('delivery.delivery_dashboard'))

        flash(t('messages.invalid_login'), 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Self sign-up for delivery users"""
    if current_user.is_authenticated:
        if current_user.role == 'delivery':
            return redirect(url_for('delivery.delivery_dashboard'))
        logout_user()
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        full_name = (request.form.get('full_name') or '').strip()
        age_raw = (request.form.get('age') or '').strip()
        gender = (request.form.get('gender') or '').strip()
        phone = (request.form.get('phone') or '').strip()
        email = (request.form.get('email') or '').strip()
        city = (request.form.get('city') or '').strip()
        password = (request.form.get('password') or '').strip()
        confirm_password = (request.form.get('confirm_password') or '').strip()

        if not all([full_name, age_raw, gender, phone, email, city, password, confirm_password]):
            flash(t('messages.fill_required'), 'warning')
            return redirect(url_for('auth.register'))

        try:
            age = int(age_raw)
            if age <= 0:
                raise ValueError('invalid age')
        except ValueError:
            flash(t('messages.valid_age'), 'warning')
            return redirect(url_for('auth.register'))

        allowed_genders = {'Male', 'Female', 'Other'}
        if gender not in allowed_genders:
            flash(t('messages.valid_gender'), 'warning')
            return redirect(url_for('auth.register'))

        if password != confirm_password:
            flash(t('messages.passwords_do_not_match'), 'danger')
            return redirect(url_for('auth.register'))

        username = phone

        if User.query.filter_by(username=username).first():
            flash(t('messages.phone_registered'), 'danger')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(email=email).first():
            flash(t('messages.email_registered'), 'danger')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(phone=phone).first():
            flash(t('messages.phone_registered'), 'danger')
            return redirect(url_for('auth.register'))

        user = User(
            username=username,
            email=email,
            full_name=full_name,
            age=age,
            gender=gender,
            phone=phone,
            city=city,
            role='delivery'
        )
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        agent = DeliveryAgent(user_id=user.id, city=city, active=False)
        db.session.add(agent)
        db.session.commit()

        flash(t('messages.account_created'), 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth_bp.route('/logout')
def logout():
    logout_user()
    flash(t('messages.logged_out'), 'info')
    return redirect(url_for('auth.login'))


# ==================== DELIVERY BLUEPRINT ====================

delivery_bp = Blueprint('delivery', __name__, url_prefix='/delivery')


@delivery_bp.route('/')
@login_required
def delivery_dashboard():
    agent = _require_delivery_agent()
    if not agent:
        return redirect(url_for('auth.login'))

    deliveries = Delivery.query.filter_by(delivery_agent_id=agent.id).order_by(
        Delivery.assigned_at.desc()
    ).all()

    assigned_count = Delivery.query.filter_by(delivery_agent_id=agent.id, status='Assigned').count()
    in_transit_count = Delivery.query.filter(
        Delivery.delivery_agent_id == agent.id,
        Delivery.status.in_(['Picked Up', 'Out for Delivery'])
    ).count()
    delivered_count = Delivery.query.filter_by(delivery_agent_id=agent.id, status='Delivered').count()

    total_earnings = db.session.query(db.func.sum(Delivery.delivery_fee)).filter_by(
        delivery_agent_id=agent.id,
        status='Delivered'
    ).scalar() or 0

    week_start = datetime.utcnow() - timedelta(days=7)
    week_earnings = db.session.query(db.func.sum(Delivery.delivery_fee)).filter(
        Delivery.delivery_agent_id == agent.id,
        Delivery.status == 'Delivered',
        Delivery.delivered_at >= week_start
    ).scalar() or 0

    pending_cash = db.session.query(db.func.sum(Delivery.cash_to_collect)).filter(
        Delivery.delivery_agent_id == agent.id,
        Delivery.status != 'Delivered'
    ).scalar() or 0

    for delivery in deliveries:
        delivery.directions_url = _build_google_maps_directions_url(delivery.order, delivery)

    return render_template(
        'delivery/dashboard.html',
        agent=agent,
        deliveries=deliveries,
        assigned_count=assigned_count,
        in_transit_count=in_transit_count,
        delivered_count=delivered_count,
        total_earnings=total_earnings,
        week_earnings=week_earnings,
        pending_cash=pending_cash
    )


@delivery_bp.route('/deliveries/<int:delivery_id>')
@login_required
def delivery_detail(delivery_id):
    agent = _require_delivery_agent()
    if not agent:
        return redirect(url_for('auth.login'))

    delivery = Delivery.query.get_or_404(delivery_id)
    if delivery.delivery_agent_id != agent.id:
        flash(t('messages.unauthorized_delivery'), 'danger')
        return redirect(url_for('delivery.delivery_dashboard'))

    updates = DeliveryStatusUpdate.query.filter_by(delivery_id=delivery.id).order_by(
        DeliveryStatusUpdate.created_at.desc()
    ).all()

    map_url = _build_google_maps_url(delivery.order, delivery)
    directions_url = _build_google_maps_directions_url(delivery.order, delivery)
    return render_template(
        'delivery/detail.html',
        delivery=delivery,
        order=delivery.order,
        updates=updates,
        map_url=map_url,
        directions_url=directions_url
    )


@delivery_bp.route('/deliveries/<int:delivery_id>/status', methods=['POST'])
@login_required
def delivery_update_status(delivery_id):
    agent = _require_delivery_agent()
    if not agent:
        return redirect(url_for('auth.login'))

    delivery = Delivery.query.get_or_404(delivery_id)
    if delivery.delivery_agent_id != agent.id:
        flash(t('messages.unauthorized_delivery'), 'danger')
        return redirect(url_for('delivery.delivery_dashboard'))

    new_status = request.form.get('status')
    allowed = {'Picked Up', 'Out for Delivery', 'Failed'}
    if new_status not in allowed:
        flash(t('messages.invalid_status'), 'warning')
        return redirect(url_for('delivery.delivery_detail', delivery_id=delivery.id))

    note = (request.form.get('note') or '').strip() or None

    now = datetime.utcnow()
    if new_status == 'Picked Up':
        delivery.picked_up_at = now
    elif new_status == 'Out for Delivery':
        delivery.out_for_delivery_at = now
    elif new_status == 'Failed' and note:
        delivery.notes = note

    delivery.status = new_status
    if delivery.order and new_status in {'Picked Up', 'Out for Delivery'}:
        delivery.order.status = 'Shipped'
    if delivery.order and new_status == 'Failed':
        delivery.order.status = 'Failed'

    db.session.add(DeliveryStatusUpdate(delivery_id=delivery.id, status=new_status, note=note))
    db.session.commit()
    flash(t('messages.delivery_status_updated'), 'success')
    return redirect(url_for('delivery.delivery_detail', delivery_id=delivery.id))


@delivery_bp.route('/deliveries/<int:delivery_id>/location', methods=['POST'])
@login_required
def delivery_update_location(delivery_id):
    agent = _require_delivery_agent()
    if not agent:
        return redirect(url_for('auth.login'))

    delivery = Delivery.query.get_or_404(delivery_id)
    if delivery.delivery_agent_id != agent.id:
        flash(t('messages.unauthorized_delivery'), 'danger')
        return redirect(url_for('delivery.delivery_dashboard'))

    lat_raw = request.form.get('lat')
    lng_raw = request.form.get('lng')
    try:
        lat = float(lat_raw)
        lng = float(lng_raw)
    except (TypeError, ValueError):
        flash(t('messages.valid_coordinates'), 'warning')
        return redirect(url_for('delivery.delivery_detail', delivery_id=delivery.id))

    delivery.last_lat = lat
    delivery.last_lng = lng
    delivery.last_location_at = datetime.utcnow()
    db.session.commit()
    flash(t('messages.location_updated'), 'success')
    return redirect(url_for('delivery.delivery_detail', delivery_id=delivery.id))


@delivery_bp.route('/deliveries/<int:delivery_id>/verify', methods=['POST'])
@login_required
def delivery_verify_otp(delivery_id):
    agent = _require_delivery_agent()
    if not agent:
        return redirect(url_for('auth.login'))

    delivery = Delivery.query.get_or_404(delivery_id)
    if delivery.delivery_agent_id != agent.id:
        flash(t('messages.unauthorized_delivery'), 'danger')
        return redirect(url_for('delivery.delivery_dashboard'))

    if delivery.status == 'Delivered':
        flash(t('messages.already_completed'), 'info')
        return redirect(url_for('delivery.delivery_detail', delivery_id=delivery.id))

    otp_code = (request.form.get('otp_code') or '').strip()
    if not otp_code or not delivery.otp_code:
        flash(t('messages.otp_required'), 'warning')
        return redirect(url_for('delivery.delivery_detail', delivery_id=delivery.id))

    if otp_code != delivery.otp_code:
        flash(t('messages.invalid_otp'), 'danger')
        return redirect(url_for('delivery.delivery_detail', delivery_id=delivery.id))

    now = datetime.utcnow()
    delivery.status = 'Delivered'
    delivery.delivered_at = now
    delivery.otp_verified_at = now
    delivery.cash_to_collect = 0.0

    if delivery.order:
        delivery.order.status = 'Delivered'
        if delivery.order.payment_method == 'Cash on Delivery' and delivery.order.payment_status != 'Paid':
            delivery.order.payment_status = 'Paid'

    db.session.add(DeliveryStatusUpdate(delivery_id=delivery.id, status='Delivered'))
    db.session.commit()
    flash(t('messages.delivery_completed'), 'success')
    return redirect(url_for('delivery.delivery_detail', delivery_id=delivery.id))
