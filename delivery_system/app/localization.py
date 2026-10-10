"""Lightweight language support for the delivery application."""

from flask import request, session

DEFAULT_LANGUAGE = 'en'

SUPPORTED_LANGUAGES = {
    'en': 'English',
    'hi': 'हिंदी',
}

TRANSLATIONS = {
    'en': {
        'app.name': 'AcuMeds Delivery',
        'nav.dashboard': 'My Deliveries',
        'nav.main_app': 'Customer Portal',
        'nav.logout': 'Logout',
        'nav.login': 'Sign In',
        'nav.register_shop': 'Sign Up',
        'nav.language': 'Language',
        'footer.copyright': '© 2026 AcuMeds Delivery. All rights reserved.',
        'footer.disclaimer': 'Delivery portal for drivers and agents.',
        'chatbot.title': 'AI Assistant',
        'chatbot.placeholder': 'Ask anything about this page...',
        'chatbot.send': 'Send',
        'chatbot.you': 'You',
        'chatbot.bot': 'Bot',
        'chatbot.no_response': 'No response received.',
        'chatbot.unavailable': 'AI service is currently unavailable. Please try again.',
        'title.home': 'Delivery Home',
        'title.login': 'Sign In',
        'title.register': 'Sign Up',
        'title.dashboard': 'Delivery Dashboard',
        'home.eyebrow': 'AcuMeds Delivery Network',
        'home.hero_title': 'Deliver medicine with calm, fast, and verified handoffs.',
        'home.hero_body': 'A focused delivery workspace for routing, proof of delivery, and daily earnings. Built for speed on the road and clarity at HQ.',
        'home.hero_note': 'New delivery accounts go live after admin approval.',
        'home.badge_otp': 'OTP verified',
        'home.badge_live_location': 'Live location',
        'home.badge_fast_payouts': 'Instant payouts',
        'home.pickup_label': 'Pickup',
        'home.drop_label': 'Drop',
        'home.eta_label': 'ETA',
        'home.otp_ready': 'OTP ready',
        'home.sign_in': 'Sign In',
        'home.create_account': 'Create account',
        'home.view_demo': 'View demo access',
        'home.live_route': 'Live Route',
        'home.active_delivery': 'Active Delivery',
        'home.pending_cash': 'Pending cash',
        'home.deliveries_today': 'Deliveries today',
        'home.avg_time': 'Avg time',
        'home.on_time': 'On time',
        'home.otp_title': 'OTP-first handoffs',
        'home.otp_body': 'Every drop is verified with an OTP to keep compliance airtight.',
        'home.route_title': 'Live route updates',
        'home.route_body': 'Share a clean status timeline with ops, shopkeepers, and customers.',
        'home.settlement_title': 'Fast settlements',
        'home.settlement_body': 'Track delivery fees and pending cash in one compact view.',
        'home.core_capabilities': 'Core capabilities',
        'home.core_title': 'Everything a delivery team needs, nothing extra.',
        'home.smart_assignment': 'Smart assignment',
        'home.smart_assignment_body': 'Ops assigns orders in seconds with clear workload visibility.',
        'home.proof_delivery': 'Proof of delivery',
        'home.proof_delivery_body': 'OTP verification and status logs keep every drop accountable.',
        'home.location_heartbeat': 'Location heartbeat',
        'home.location_heartbeat_body': 'Update GPS coordinates and keep the team synced in real time.',
        'home.how_it_works': 'How it works',
        'home.three_step': 'Three-step delivery flow.',
        'home.assign': 'Assign',
        'home.assign_body': 'Admin assigns a delivery agent and OTP is generated instantly.',
        'home.deliver': 'Deliver',
        'home.deliver_body': 'Agent updates status, shares location, and reaches the customer.',
        'home.verify': 'Verify',
        'home.verify_body': 'OTP verified, order completed, earnings updated instantly.',
        'home.ready': 'Ready to sign in?',
        'home.ready_body': 'Use demo delivery credentials or create a new account.',
        'home.demo_delivery': 'Delivery',
        'home.new_delivery': 'New delivery',
        'home.create_delivery_account': 'Create a new delivery account',
        'home.demo_note': 'New delivery accounts need admin approval.',
        'auth.sign_in_title': 'Sign In',
        'auth.identity': 'Email, Phone, or Username',
        'auth.password': 'Password',
        'auth.demo_delivery': 'Demo Delivery',
        'auth.note': 'New delivery accounts need admin approval.',
        'auth.create_new': 'Create a new delivery account',
        'auth.create_title': 'Create Delivery Account',
        'auth.full_name': 'Full Name',
        'auth.age': 'Age',
        'auth.gender': 'Gender',
        'auth.select': 'Select',
        'auth.male': 'Male',
        'auth.female': 'Female',
        'auth.other': 'Other',
        'auth.phone': 'Phone',
        'auth.email': 'Email',
        'auth.city': 'City',
        'auth.confirm_password': 'Confirm Password',
        'auth.create_account_button': 'Create Account',
        'auth.approval_note': 'Your account will be active after admin approval.',
        'auth.already_account': 'Already have an account? Sign in',
        'dashboard.title': 'Delivery Dashboard',
        'dashboard.reminder': 'Delivery Reminder',
        'dashboard.pending_message': '{count} order(s) pending for delivery/process.',
        'dashboard.enable_notification': 'Enable Browser Notification',
        'dashboard.assigned': 'Assigned',
        'dashboard.in_transit': 'In Transit',
        'dashboard.delivered': 'Delivered',
        'dashboard.weekly_earnings': 'Weekly Earnings',
        'dashboard.assigned_deliveries': 'Assigned Deliveries',
        'dashboard.pending_cash': 'Pending Cash',
        'dashboard.quick_map': 'Quick Map Guide:',
        'dashboard.quick_map_body': 'Tap Navigate to start the route. Open the delivery details if you need more order information.',
        'dashboard.refresh_note': 'Dashboard har 30 second me auto-refresh hota hai.',
        'dashboard.status_assigned': 'Assigned',
        'dashboard.status_picked_up': 'Picked Up',
        'dashboard.status_out_for_delivery': 'Out for Delivery',
        'dashboard.status_delivered': 'Delivered',
        'dashboard.status_failed': 'Failed',
        'dashboard.order': 'Order',
        'dashboard.customer': 'Customer',
        'dashboard.status': 'Status',
        'dashboard.cash': 'Cash',
        'dashboard.assigned_at': 'Assigned',
        'dashboard.route_actions': 'Route Actions',
        'dashboard.action': 'Action',
        'dashboard.view': 'View',
        'dashboard.navigate': 'Navigate',
        'dashboard.navigate_note': 'Open the route in Google Maps to start navigation.',
        'dashboard.location_unavailable': 'Location not available yet.',
        'dashboard.notification_title': 'AcuMeds Delivery Alert',
        'dashboard.notification_single': '1 delivery is pending. Please open the dashboard and complete it.',
        'dashboard.notification_plural': '{count} deliveries are pending. Please open the dashboard and complete them.',
        'dashboard.total_earnings': 'Total Earnings',
        'messages.only_delivery_portal': 'Only delivery accounts can access this portal.',
        'messages.only_delivery_signin': 'Only delivery accounts can sign in here.',
        'messages.pending_approval': 'Your account is pending admin approval.',
        'messages.invalid_login': 'Invalid email/username or password',
        'messages.fill_required': 'Please fill in all required fields.',
        'messages.valid_age': 'Please provide a valid age.',
        'messages.valid_gender': 'Please select a valid gender.',
        'messages.passwords_do_not_match': 'Passwords do not match.',
        'messages.phone_registered': 'Phone number already registered.',
        'messages.email_registered': 'Email already registered.',
        'messages.account_created': 'Account created. Awaiting admin approval.',
        'messages.logged_out': 'You have been logged out.',
        'messages.delivery_access_required': 'Delivery access required',
        'messages.delivery_account_inactive': 'Your delivery account is inactive.',
        'messages.unauthorized_delivery': 'Unauthorized delivery access',
        'messages.invalid_status': 'Invalid delivery status',
        'messages.delivery_status_updated': 'Delivery status updated successfully.',
        'messages.valid_coordinates': 'Please provide valid latitude and longitude.',
        'messages.location_updated': 'Location updated successfully.',
        'messages.already_completed': 'This delivery is already completed.',
        'messages.otp_required': 'OTP is required to complete delivery.',
        'messages.invalid_otp': 'Invalid OTP. Please try again.',
        'messages.delivery_completed': 'Delivery completed successfully.',
        'messages.enter_question': 'Please type a question first.',
        'messages.language_changed': 'Language changed to {language}.',
    },
    'hi': {
        'app.name': 'AcuMeds Delivery',
        'nav.dashboard': 'मेरी डिलीवरी',
        'nav.main_app': 'कस्टमर पोर्टल',
        'nav.logout': 'लॉग आउट',
        'nav.login': 'साइन इन',
        'nav.register_shop': 'साइन अप',
        'nav.language': 'भाषा',
        'footer.copyright': '© 2026 AcuMeds Delivery. सभी अधिकार सुरक्षित।',
        'footer.disclaimer': 'ड्राइवर और एजेंटों के लिए डिलीवरी पोर्टल।',
        'chatbot.title': 'AI सहायक',
        'chatbot.placeholder': 'इस पृष्ठ के बारे में कुछ भी पूछें...',
        'chatbot.send': 'भेजें',
        'chatbot.you': 'आप',
        'chatbot.bot': 'बॉट',
        'chatbot.no_response': 'कोई उत्तर नहीं मिला।',
        'chatbot.unavailable': 'AI सेवा अभी उपलब्ध नहीं है। कृपया फिर से प्रयास करें।',
        'title.home': 'डिलीवरी होम',
        'title.login': 'साइन इन',
        'title.register': 'साइन अप',
        'title.dashboard': 'डिलीवरी डैशबोर्ड',
        'home.eyebrow': 'AcuMeds डिलीवरी नेटवर्क',
        'home.hero_title': 'दवाइयाँ शांत, तेज़ और सत्यापित तरीके से पहुँचाएँ।',
        'home.hero_body': 'रूटिंग, डिलीवरी प्रमाण और दैनिक कमाई के लिए एक केंद्रित डिलीवरी वर्कस्पेस। रास्ते में गति और HQ में स्पष्टता के लिए बनाया गया।',
        'home.hero_note': 'नए डिलीवरी खाते एडमिन अनुमोदन के बाद सक्रिय होते हैं।',
        'home.badge_otp': 'OTP सत्यापित',
        'home.badge_live_location': 'लाइव लोकेशन',
        'home.badge_fast_payouts': 'तुरंत भुगतान',
        'home.pickup_label': 'पिकअप',
        'home.drop_label': 'ड्रॉप',
        'home.eta_label': 'अनुमानित समय',
        'home.otp_ready': 'OTP तैयार',
        'home.sign_in': 'साइन इन',
        'home.create_account': 'खाता बनाएं',
        'home.view_demo': 'डेमो एक्सेस देखें',
        'home.live_route': 'लाइव रूट',
        'home.active_delivery': 'सक्रिय डिलीवरी',
        'home.pending_cash': 'बकाया नकद',
        'home.deliveries_today': 'आज की डिलीवरी',
        'home.avg_time': 'औसत समय',
        'home.on_time': 'समय पर',
        'home.otp_title': 'OTP-प्रथम हैंडऑफ़',
        'home.otp_body': 'हर डिलीवरी OTP से सत्यापित होती है ताकि अनुपालन सख्त रहे।',
        'home.route_title': 'लाइव रूट अपडेट',
        'home.route_body': 'ऑप्स, शॉपकीपर और ग्राहकों के साथ साफ़ स्थिति टाइमलाइन साझा करें।',
        'home.settlement_title': 'तेज़ निपटान',
        'home.settlement_body': 'डिलीवरी शुल्क और बकाया नकद को एक कॉम्पैक्ट दृश्य में ट्रैक करें।',
        'home.core_capabilities': 'मुख्य क्षमताएँ',
        'home.core_title': 'डिलीवरी टीम को जो चाहिए, बस वही।',
        'home.smart_assignment': 'स्मार्ट असाइनमेंट',
        'home.smart_assignment_body': 'ऑप्स साफ़ वर्कलोड दृश्यता के साथ कुछ सेकंड में ऑर्डर असाइन करता है।',
        'home.proof_delivery': 'डिलीवरी प्रमाण',
        'home.proof_delivery_body': 'OTP सत्यापन और स्टेटस लॉग हर डिलीवरी को जवाबदेह रखते हैं।',
        'home.location_heartbeat': 'लोकेशन हार्टबीट',
        'home.location_heartbeat_body': 'GPS कोऑर्डिनेट अपडेट करें और टीम को रीयल-टाइम में सिंक रखें।',
        'home.how_it_works': 'यह कैसे काम करता है',
        'home.three_step': 'तीन-चरणीय डिलीवरी फ़्लो।',
        'home.assign': 'असाइन',
        'home.assign_body': 'एडमिन डिलीवरी एजेंट असाइन करता है और OTP तुरंत बनता है।',
        'home.deliver': 'डिलीवर',
        'home.deliver_body': 'एजेंट स्टेटस अपडेट करता है, लोकेशन साझा करता है और ग्राहक तक पहुँचता है।',
        'home.verify': 'सत्यापित करें',
        'home.verify_body': 'OTP सत्यापित, ऑर्डर पूरा, कमाई तुरंत अपडेट।',
        'home.ready': 'साइन इन करने के लिए तैयार?',
        'home.ready_body': 'डेमो क्रेडेंशियल्स इस्तेमाल करें या नया खाता बनाएं।',
        'home.demo_delivery': 'डिलीवरी',
        'home.new_delivery': 'नई डिलीवरी',
        'home.create_delivery_account': 'नया डिलीवरी खाता बनाएं',
        'home.demo_note': 'नए डिलीवरी खातों को एडमिन अनुमोदन चाहिए।',
        'auth.sign_in_title': 'साइन इन',
        'auth.identity': 'ईमेल, फ़ोन, या उपयोगकर्ता नाम',
        'auth.password': 'पासवर्ड',
        'auth.demo_delivery': 'डेमो डिलीवरी',
        'auth.note': 'नए डिलीवरी खातों को एडमिन अनुमोदन चाहिए।',
        'auth.create_new': 'नया डिलीवरी खाता बनाएं',
        'auth.create_title': 'डिलीवरी खाता बनाएं',
        'auth.full_name': 'पूरा नाम',
        'auth.age': 'आयु',
        'auth.gender': 'लिंग',
        'auth.select': 'चुनें',
        'auth.male': 'पुरुष',
        'auth.female': 'महिला',
        'auth.other': 'अन्य',
        'auth.phone': 'फ़ोन',
        'auth.email': 'ईमेल',
        'auth.city': 'शहर',
        'auth.confirm_password': 'पासवर्ड की पुष्टि करें',
        'auth.create_account_button': 'खाता बनाएं',
        'auth.approval_note': 'एडमिन अनुमोदन के बाद आपका खाता सक्रिय होगा।',
        'auth.already_account': 'क्या आपके पास पहले से खाता है? साइन इन करें',
        'dashboard.title': 'डिलीवरी डैशबोर्ड',
        'dashboard.reminder': 'डिलीवरी रिमाइंडर',
        'dashboard.pending_message': '{count} ऑर्डर डिलीवरी/प्रोसेस के लिए लंबित हैं।',
        'dashboard.enable_notification': 'ब्राउज़र नोटिफिकेशन सक्षम करें',
        'dashboard.assigned': 'असाइन',
        'dashboard.in_transit': 'रास्ते में',
        'dashboard.delivered': 'डिलीवर',
        'dashboard.weekly_earnings': 'साप्ताहिक कमाई',
        'dashboard.assigned_deliveries': 'असाइन की गई डिलीवरी',
        'dashboard.pending_cash': 'बकाया नकद',
        'dashboard.quick_map': 'त्वरित मानचित्र गाइड:',
        'dashboard.quick_map_body': 'Route start karne ke liye Navigate दबाएँ. ज़रूरत हो तो delivery details खोलें.',
        'dashboard.refresh_note': 'डैशबोर्ड हर 30 सेकंड में ऑटो-रिफ्रेश होता है।',
        'dashboard.status_assigned': 'असाइन',
        'dashboard.status_picked_up': 'पिकअप किया गया',
        'dashboard.status_out_for_delivery': 'डिलीवरी के लिए रवाना',
        'dashboard.status_delivered': 'डिलीवर',
        'dashboard.status_failed': 'असफल',
        'dashboard.order': 'ऑर्डर',
        'dashboard.customer': 'ग्राहक',
        'dashboard.status': 'स्थिति',
        'dashboard.cash': 'नकद',
        'dashboard.assigned_at': 'असाइन किया गया',
        'dashboard.route_actions': 'रूट एक्शन',
        'dashboard.action': 'एक्शन',
        'dashboard.view': 'देखें',
        'dashboard.navigate': 'Navigate',
        'dashboard.navigate_note': 'Google Maps में route खोलकर navigation शुरू करें।',
        'dashboard.location_unavailable': 'लोकेशन अभी उपलब्ध नहीं है।',
        'dashboard.notification_title': 'AcuMeds डिलीवरी अलर्ट',
        'dashboard.notification_single': '1 डिलीवरी लंबित है। कृपया डैशबोर्ड खोलकर उसे पूरा करें।',
        'dashboard.notification_plural': '{count} डिलीवरी लंबित हैं। कृपया डैशबोर्ड खोलकर उन्हें पूरा करें।',
        'dashboard.total_earnings': 'कुल कमाई',
        'messages.only_delivery_portal': 'केवल डिलीवरी खाते इस पोर्टल तक पहुँच सकते हैं।',
        'messages.only_delivery_signin': 'केवल डिलीवरी खाते यहाँ साइन इन कर सकते हैं।',
        'messages.pending_approval': 'आपका खाता एडमिन अनुमोदन के लिए लंबित है।',
        'messages.invalid_login': 'अमान्य ईमेल/उपयोगकर्ता नाम या पासवर्ड',
        'messages.fill_required': 'कृपया सभी आवश्यक फ़ील्ड भरें।',
        'messages.valid_age': 'कृपया वैध आयु दर्ज करें।',
        'messages.valid_gender': 'कृपया वैध लिंग चुनें।',
        'messages.passwords_do_not_match': 'पासवर्ड मेल नहीं खाते।',
        'messages.phone_registered': 'फ़ोन नंबर पहले से पंजीकृत है।',
        'messages.email_registered': 'ईमेल पहले से पंजीकृत है।',
        'messages.account_created': 'खाता बन गया है। एडमिन अनुमोदन की प्रतीक्षा है।',
        'messages.logged_out': 'आप लॉग आउट हो गए हैं।',
        'messages.delivery_access_required': 'डिलीवरी एक्सेस आवश्यक है',
        'messages.delivery_account_inactive': 'आपका डिलीवरी खाता निष्क्रिय है।',
        'messages.unauthorized_delivery': 'अनधिकृत डिलीवरी एक्सेस',
        'messages.invalid_status': 'अमान्य डिलीवरी स्थिति',
        'messages.delivery_status_updated': 'डिलीवरी स्थिति सफलतापूर्वक अपडेट की गई।',
        'messages.valid_coordinates': 'कृपया वैध अक्षांश और देशांतर दर्ज करें।',
        'messages.location_updated': 'लोकेशन सफलतापूर्वक अपडेट की गई।',
        'messages.already_completed': 'यह डिलीवरी पहले ही पूरी हो चुकी है।',
        'messages.otp_required': 'डिलीवरी पूरी करने के लिए OTP आवश्यक है।',
        'messages.invalid_otp': 'अमान्य OTP। कृपया फिर से प्रयास करें।',
        'messages.delivery_completed': 'डिलीवरी सफलतापूर्वक पूरी हो गई।',
        'messages.enter_question': 'कृपया पहले एक प्रश्न टाइप करें।',
        'messages.language_changed': 'भाषा {language} में बदल दी गई है।',
    },
}

MESSAGE_KEYS = [key for key in TRANSLATIONS['en'] if key.startswith('messages.')]

MESSAGE_TRANSLATIONS = {
    language_code: {
        TRANSLATIONS['en'][key]: TRANSLATIONS[language_code][key]
        for key in MESSAGE_KEYS
        if key in TRANSLATIONS.get(language_code, {})
    }
    for language_code in SUPPORTED_LANGUAGES
}


def normalize_language(language_code):
    if language_code in SUPPORTED_LANGUAGES:
        return language_code
    return DEFAULT_LANGUAGE


def get_current_language():
    saved_language = session.get('language')
    if saved_language:
        return normalize_language(saved_language)

    accept_languages = getattr(request, 'accept_languages', None)
    if accept_languages:
        matched = accept_languages.best_match(list(SUPPORTED_LANGUAGES.keys()))
        if matched:
            return matched

    return DEFAULT_LANGUAGE


def set_current_language(language_code):
    session['language'] = normalize_language(language_code)
    return session['language']


def get_language_options():
    return [(code, label) for code, label in SUPPORTED_LANGUAGES.items()]


def get_language_label(language_code=None):
    normalized = normalize_language(language_code or get_current_language())
    return SUPPORTED_LANGUAGES[normalized]


def translate(key, **kwargs):
    language_code = get_current_language()
    language_catalog = TRANSLATIONS.get(language_code, TRANSLATIONS[DEFAULT_LANGUAGE])
    text = language_catalog.get(key, TRANSLATIONS[DEFAULT_LANGUAGE].get(key, key))
    if kwargs:
        return text.format(**kwargs)
    return text


def translate_message(message, **kwargs):
    language_code = get_current_language()
    translated = MESSAGE_TRANSLATIONS.get(language_code, {}).get(message, message)
    if kwargs:
        return translated.format(**kwargs)
    return translated
