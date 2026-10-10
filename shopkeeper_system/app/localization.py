"""Lightweight language support for the shopkeeper application."""

from flask import request, session

DEFAULT_LANGUAGE = 'en'

SUPPORTED_LANGUAGES = {
    'en': 'English',
    'hi': 'हिंदी',
}

TRANSLATIONS = {
    'en': {
        'app.name': 'AcuMeds Shopkeeper',
        'app.tagline': 'Manage your medicine shop in less time.',
        'nav.dashboard': 'Dashboard',
        'nav.my_medicines': 'My Medicines',
        'nav.orders': 'Orders',
        'nav.notifications': 'Notifications',
        'nav.ratings': 'Ratings',
        'nav.logout': 'Logout',
        'nav.login': 'Login',
        'nav.register_shop': 'Register Shop',
        'nav.main_app': 'Main App',
        'nav.language': 'Language',
        'footer.copyright': '© 2026 AcuMeds Shopkeeper Portal. All rights reserved.',
        'footer.disclaimer': 'Portal for approved medicine shop owners to manage inventory and orders.',
        'chatbot.title': 'AI Assistant',
        'chatbot.placeholder': 'Ask anything about this page...',
        'chatbot.send': 'Send',
        'chatbot.you': 'You',
        'chatbot.bot': 'Bot',
        'chatbot.no_response': 'No response received.',
        'chatbot.unavailable': 'AI service is currently unavailable. Please try again.',
        'title.login': 'Shopkeeper Login',
        'title.register': 'Shop Registration',
        'title.dashboard': 'Dashboard',
        'title.profile': 'Profile',
        'title.home': 'Home',
        'auth.portal_title': 'Shopkeeper Portal',
        'auth.manage_shop': 'Manage your medicine shop',
        'auth.email_or_username': 'Email Address or Username',
        'auth.password': 'Password',
        'auth.login': 'Login',
        'auth.no_account': "Don't have an account?",
        'auth.register_here': 'Register your shop here',
        'auth.register_pharmacy': 'Register Your Pharmacy',
        'auth.join_customers': 'Join AcuMeds and reach thousands of customers',
        'auth.full_name': 'Your Full Name *',
        'auth.shop_name': 'Shop/Pharmacy Name *',
        'auth.email': 'Email Address *',
        'auth.username': 'Username *',
        'auth.password_hint': 'At least 6 characters',
        'auth.contact_number': 'Contact Number *',
        'auth.license_number': 'License Number *',
        'auth.city': 'City',
        'auth.important': 'Important',
        'auth.verification_note': 'Your shop details will be verified by our admin team. You will receive an email once your registration is approved.',
        'auth.register_now': 'Register Now',
        'auth.already_have_account': 'Already have an account?',
        'auth.login_here': 'Login here',
        'auth.back_to_main_app': 'Back to Main App',
        'dashboard.shop_dashboard': 'Shop Dashboard',
        'dashboard.add_medicine': 'Add Medicine',
        'dashboard.profile': 'Profile',
        'dashboard.pending_verification': 'Pending Verification',
        'dashboard.pending_message': 'Your shop is awaiting admin verification. Once approved, your medicines will be visible to customers.',
        'dashboard.total_medicines': 'Total Medicines',
        'dashboard.total_stock': 'Total Stock',
        'dashboard.orders_received': 'Orders Received',
        'dashboard.total_revenue': 'Total Revenue',
        'dashboard.quick_actions': 'Quick Actions',
        'dashboard.manage_medicines': 'Manage Medicines',
        'dashboard.manage_medicines_desc': 'View and manage your medicine catalog',
        'dashboard.view_orders': 'View Orders',
        'dashboard.view_orders_desc': 'See customer orders containing your medicines',
        'dashboard.main_app': 'Main App',
        'dashboard.main_app_desc': 'Visit the customer portal',
        'dashboard.shop_information': 'Shop Information',
        'dashboard.shop_name': 'Shop Name',
        'dashboard.license': 'License',
        'dashboard.city': 'City',
        'dashboard.contact': 'Contact',
        'dashboard.not_specified': 'Not specified',
        'dashboard.status': 'Status',
        'dashboard.verified': 'Verified',
        'dashboard.pending_approval': 'Pending Approval',
        'messages.language_changed': 'Language changed to {language}.',
        'messages.login_successful': 'Login successful!',
        'messages.invalid_credentials': 'Invalid email/username or password',
        'messages.fill_required_fields': 'Please fill in all required fields',
        'messages.username_exists': 'Username already exists',
        'messages.email_exists': 'Email already exists',
        'messages.shopkeeper_profile_missing': 'Shopkeeper profile not found. Please contact support.',
        'messages.database_error': 'Database connection error. Please try again.',
        'messages.login_required': 'Please log in to access this page',
        'messages.welcome_user': 'Welcome, {name}!',
        'messages.registration_successful': 'Registration successful! You can now login.',
        'messages.registration_failed': 'Registration failed: {error}',
        'messages.logged_out': 'You have been logged out.',
    },
    'hi': {
        'app.name': 'AcuMeds शॉपकीपर',
        'app.tagline': 'अपनी दवा दुकान कम समय में संभालें।',
        'nav.dashboard': 'डैशबोर्ड',
        'nav.my_medicines': 'मेरी दवाइयाँ',
        'nav.orders': 'ऑर्डर',
        'nav.notifications': 'सूचनाएँ',
        'nav.ratings': 'रेटिंग्स',
        'nav.logout': 'लॉग आउट',
        'nav.login': 'लॉगिन',
        'nav.register_shop': 'दुकान रजिस्टर करें',
        'nav.main_app': 'मुख्य ऐप',
        'nav.language': 'भाषा',
        'footer.copyright': '© 2026 AcuMeds शॉपकीपर पोर्टल। सभी अधिकार सुरक्षित।',
        'footer.disclaimer': 'अनुमोदित दवा दुकान मालिकों के लिए इन्वेंटरी और ऑर्डर प्रबंधन पोर्टल।',
        'chatbot.title': 'AI सहायक',
        'chatbot.placeholder': 'इस पृष्ठ के बारे में कुछ भी पूछें...',
        'chatbot.send': 'भेजें',
        'chatbot.you': 'आप',
        'chatbot.bot': 'बॉट',
        'chatbot.no_response': 'कोई उत्तर नहीं मिला।',
        'chatbot.unavailable': 'AI सेवा अभी उपलब्ध नहीं है। कृपया फिर से प्रयास करें।',
        'title.login': 'शॉपकीपर लॉगिन',
        'title.register': 'दुकान पंजीकरण',
        'title.dashboard': 'डैशबोर्ड',
        'title.profile': 'प्रोफ़ाइल',
        'title.home': 'होम',
        'auth.portal_title': 'शॉपकीपर पोर्टल',
        'auth.manage_shop': 'अपनी दवा दुकान संभालें',
        'auth.email_or_username': 'ईमेल पता या उपयोगकर्ता नाम',
        'auth.password': 'पासवर्ड',
        'auth.login': 'लॉगिन',
        'auth.no_account': 'क्या आपके पास खाता नहीं है?',
        'auth.register_here': 'अपनी दुकान यहाँ रजिस्टर करें',
        'auth.register_pharmacy': 'अपनी फ़ार्मेसी रजिस्टर करें',
        'auth.join_customers': 'AcuMeds से जुड़ें और हज़ारों ग्राहकों तक पहुँचें',
        'auth.full_name': 'आपका पूरा नाम *',
        'auth.shop_name': 'दुकान/फ़ार्मेसी का नाम *',
        'auth.email': 'ईमेल पता *',
        'auth.username': 'उपयोगकर्ता नाम *',
        'auth.password_hint': 'कम से कम 6 अक्षर',
        'auth.contact_number': 'संपर्क नंबर *',
        'auth.license_number': 'लाइसेंस नंबर *',
        'auth.city': 'शहर',
        'auth.important': 'महत्वपूर्ण',
        'auth.verification_note': 'आपके दुकान विवरण की जाँच हमारी प्रशासनिक टीम करेगी। पंजीकरण स्वीकृत होने पर आपको ईमेल मिलेगा।',
        'auth.register_now': 'अभी रजिस्टर करें',
        'auth.already_have_account': 'क्या आपके पास पहले से खाता है?',
        'auth.login_here': 'यहाँ लॉगिन करें',
        'auth.back_to_main_app': 'मुख्य ऐप पर वापस जाएँ',
        'dashboard.shop_dashboard': 'शॉप डैशबोर्ड',
        'dashboard.add_medicine': 'दवा जोड़ें',
        'dashboard.profile': 'प्रोफ़ाइल',
        'dashboard.pending_verification': 'सत्यापन लंबित',
        'dashboard.pending_message': 'आपकी दुकान प्रशासनिक सत्यापन की प्रतीक्षा कर रही है। स्वीकृत होने पर आपकी दवाइयाँ ग्राहकों को दिखेंगी।',
        'dashboard.total_medicines': 'कुल दवाइयाँ',
        'dashboard.total_stock': 'कुल स्टॉक',
        'dashboard.orders_received': 'प्राप्त ऑर्डर',
        'dashboard.total_revenue': 'कुल आय',
        'dashboard.quick_actions': 'त्वरित कार्य',
        'dashboard.manage_medicines': 'दवाइयाँ प्रबंधित करें',
        'dashboard.manage_medicines_desc': 'अपनी दवा सूची देखें और प्रबंधित करें',
        'dashboard.view_orders': 'ऑर्डर देखें',
        'dashboard.view_orders_desc': 'अपनी दवाइयों वाले ग्राहक ऑर्डर देखें',
        'dashboard.main_app': 'मुख्य ऐप',
        'dashboard.main_app_desc': 'ग्राहक पोर्टल पर जाएँ',
        'dashboard.shop_information': 'दुकान की जानकारी',
        'dashboard.shop_name': 'दुकान का नाम',
        'dashboard.license': 'लाइसेंस',
        'dashboard.city': 'शहर',
        'dashboard.contact': 'संपर्क',
        'dashboard.not_specified': 'उल्लेखित नहीं',
        'dashboard.status': 'स्थिति',
        'dashboard.verified': 'सत्यापित',
        'dashboard.pending_approval': 'स्वीकृति लंबित',
        'messages.language_changed': 'भाषा {language} में बदल दी गई है।',
        'messages.login_successful': 'लॉगिन सफल रहा!',
        'messages.invalid_credentials': 'अमान्य ईमेल/उपयोगकर्ता नाम या पासवर्ड',
        'messages.fill_required_fields': 'कृपया सभी आवश्यक फ़ील्ड भरें',
        'messages.username_exists': 'उपयोगकर्ता नाम पहले से मौजूद है',
        'messages.email_exists': 'ईमेल पहले से मौजूद है',
        'messages.shopkeeper_profile_missing': 'शॉपकीपर प्रोफ़ाइल नहीं मिली। कृपया सहायता से संपर्क करें।',
        'messages.database_error': 'डेटाबेस कनेक्शन त्रुटि। कृपया फिर प्रयास करें।',
        'messages.login_required': 'इस पृष्ठ तक पहुँचने के लिए लॉगिन करें',
        'messages.welcome_user': 'स्वागत है, {name}!',
        'messages.registration_successful': 'पंजीकरण सफल रहा! अब आप लॉगिन कर सकते हैं।',
        'messages.registration_failed': 'पंजीकरण विफल: {error}',
        'messages.logged_out': 'आप लॉग आउट हो गए हैं।',
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


def get_language_label(language_code=None):
    normalized = normalize_language(language_code or get_current_language())
    return SUPPORTED_LANGUAGES[normalized]


def get_language_options():
    return [(code, label) for code, label in SUPPORTED_LANGUAGES.items()]


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