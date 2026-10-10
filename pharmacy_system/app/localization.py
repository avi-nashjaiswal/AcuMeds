"""Lightweight language support for the pharmacy application."""

from flask import request, session

DEFAULT_LANGUAGE = 'en'

SUPPORTED_LANGUAGES = {
    'en': 'English',
    'hi': 'हिंदी',
}

TRANSLATIONS = {
    'en': {
        'app.name': 'AcuMeds',
        'app.tagline': 'AI-assisted medicine recommendations, fast home delivery, and effortless refills.',
        'nav.shop_medicines': 'Shop Medicines',
        'nav.vendors': 'Vendors',
        'nav.symptom_check': 'AI Symptom Check',
        'nav.cart': 'Cart',
        'nav.delivery_panel': 'Delivery Panel',
        'nav.profile_settings': 'Profile / Settings',
        'nav.my_recommendations': 'My Recommendations',
        'nav.my_orders': 'My Orders',
        'nav.doctor_appointments': 'Doctor Appointments',
        'nav.digital_prescriptions': 'Digital Prescriptions',
        'nav.consult_doctor': 'Consult Doctor',
        'nav.dashboard': 'Dashboard',
        'nav.logout': 'Logout',
        'nav.login': 'Login',
        'nav.register': 'Register',
        'nav.language': 'Language',
        'footer.copyright': '© 2026 AcuMeds. All Rights Reserved.',
        'footer.disclaimer': 'Disclaimer: This is a demo application. Always consult healthcare professionals for medical advice.',
        'chatbot.title': 'AI Assistant',
        'chatbot.placeholder': 'Ask anything about this page...',
        'chatbot.send': 'Send',
        'chatbot.you': 'You',
        'chatbot.bot': 'Bot',
        'chatbot.no_response': 'No response received.',
        'chatbot.unavailable': 'AI service is currently unavailable. Please try again.',
        'title.login': 'Login',
        'title.register': 'Register',
        'title.forgot_password': 'Forgot Password',
        'title.reset_password': 'Reset Password',
        'title.home': 'Home',
        'title.dashboard': 'Dashboard',
        'auth.username_or_email': 'Username or Email',
        'auth.password': 'Password',
        'auth.forgot_password': 'Forgot Password?',
        'auth.no_account': "Don't have an account?",
        'auth.already_have_account': 'Already have an account?',
        'auth.login_here': 'Login here',
        'auth.register_here': 'Register here',
        'auth.demo_credentials': 'Demo Credentials',
        'auth.email_address': 'Email Address',
        'auth.create_account': 'Create Account',
        'auth.confirm_password': 'Confirm Password',
        'auth.password_hint': 'Password must be at least 8 characters long.',
        'auth.back_to_login': 'Back to Login',
        'auth.enter_email': 'Enter your email address',
        'auth.email_help': "We'll send a password reset link to this email.",
        'auth.send_reset_link': 'Send Reset Link',
        'auth.new_password': 'New Password',
        'auth.confirm_new_password': 'Confirm New Password',
        'auth.set_new_password': 'Set New Password',
        'auth.username': 'Username',
        'home.hero_title': 'AcuMeds',
        'home.hero_tagline': 'AI-assisted medicine recommendations, fast home delivery, and effortless refills - care that comes to you.',
        'home.primary_cta': 'Go to Dashboard',
        'home.secondary_cta': 'Login / Register',
        'home.symptom_cta': 'Check Symptoms',
        'home.quick_symptom_title': 'Quick symptom check',
        'home.quick_symptom_body': 'Type your symptoms and get recommended medicines instantly.',
        'home.ai_match': 'AI Match: 75%',
        'home.feature_ai_title': 'AI Recommendations',
        'home.feature_ai_body': 'Describe symptoms and get suggested medicines instantly with explainable reasons.',
        'home.feature_delivery_title': 'Fast Delivery',
        'home.feature_delivery_body': 'Order confirmations and home delivery in 2-5 business days.',
        'home.feature_refill_title': 'Refill Subscriptions',
        'home.feature_refill_body': 'Auto-refill your essential medicines on a schedule you control.',
        'home.shopkeeper_title': 'Are you a Pharmacy Owner?',
        'home.shopkeeper_body': 'Join AcuMeds and expand your business reach. Start selling medicines online in minutes.',
        'home.shopkeeper_cta': 'Register Your Shop',
        'home.welcome_banner': 'Welcome to MediCare Pharmacy',
        'home.welcome_text': 'Your trusted online pharmacy for all your medical needs',
        'home.order_text': 'Order medicines online with prescription verification and fast delivery',
        'home.shop_now': 'Shop Now',
        'home.ai_check': 'AI Symptom Check',
        'home.secure_title': 'Secure & Safe',
        'home.secure_body': 'All transactions are encrypted and secure. Your data is protected.',
        'home.delivery_title': 'Fast Delivery',
        'home.delivery_body': 'Get your medicines delivered within 5 days to your doorstep.',
        'home.ai_title': 'AI Recommendations',
        'home.ai_body': 'Get medicine recommendations based on your symptoms instantly.',
        'home.featured_medicines': 'Featured Medicines',
        'home.view_details': 'View Details',
        'home.add_to_cart': 'Add to Cart',
        'home.out_of_stock': 'Out of Stock',
        'home.requires_prescription': 'Requires Prescription',
        'home.browse_all': 'Browse All Medicines',
        'dashboard.welcome': 'Welcome, {name}!',
        'dashboard.edit_profile': 'Edit Profile',
        'dashboard.items_in_cart': 'Items in Cart',
        'dashboard.total_orders': 'Total Orders',
        'dashboard.symptom_checks': 'Symptom Checks',
        'dashboard.ai_recommendations': 'AI Recommendations',
        'dashboard.recent_orders': 'Recent Orders',
        'dashboard.recent_symptom_checks': 'Recent Symptom Checks',
        'dashboard.recent_recommendations': 'Recommended For You',
        'dashboard.view': 'View',
        'dashboard.view_all': 'View All',
        'dashboard.order_id': 'Order ID',
        'dashboard.date': 'Date',
        'dashboard.amount': 'Amount',
        'dashboard.status': 'Status',
        'dashboard.symptoms': 'Symptoms',
        'dashboard.no_orders': 'No orders yet.',
        'dashboard.no_recommendations': 'No recommendations yet.',
        'dashboard.recommendation_empty': 'Start placing orders to get personalized recommendations!',
        'dashboard.loading': 'Loading recommendations...',
        'dashboard.browse_medicines': 'Browse Medicines',
        'dashboard.try_now': 'Try Now',
        'messages.language_changed': 'Language changed to {language}.',
        'messages.login_successful': 'Login successful!',
        'messages.account_created': 'Account created successfully!',
        'messages.logged_out': 'You have been logged out',
        'messages.invalid_credentials': 'Invalid username or password',
        'messages.account_deactivated': 'Your account has been deactivated. Please contact support.',
        'messages.all_fields_required': 'All fields are required',
        'messages.passwords_do_not_match': 'Passwords do not match',
        'messages.username_exists': 'Username already exists',
        'messages.email_exists': 'Email already registered',
        'messages.reset_link_sent': 'Password reset link sent to your email',
        'messages.reset_link_maybe_sent': 'If an account with that email exists, a reset link will be sent',
        'messages.enter_question_first': 'Please type a question first.',
        'messages.start_shopping': 'Start shopping!',
        'messages.try_ai_checker': 'Try our AI symptom checker!',
        'messages.browse_medicines': 'Browse Medicines',
        'messages.no_orders_yet': 'No orders yet.',
        'messages.no_recommendations_yet': 'No recommendations yet.',
        'messages.start_orders_for_recommendations': 'Start placing orders to get personalized recommendations!',
        'messages.loading_recommendations': 'Loading recommendations...',
        'messages.error_loading_recommendations': 'Error loading recommendations',
    },
    'hi': {
        'app.name': 'AcuMeds',
        'app.tagline': 'AI-संचालित दवा सुझाव, तेज़ होम डिलीवरी और आसान रीफ़िल।',
        'nav.shop_medicines': 'दवाइयाँ खरीदें',
        'nav.vendors': 'विक्रेता',
        'nav.symptom_check': 'AI लक्षण जाँच',
        'nav.cart': 'कार्ट',
        'nav.delivery_panel': 'डिलीवरी पैनल',
        'nav.profile_settings': 'प्रोफ़ाइल / सेटिंग्स',
        'nav.my_recommendations': 'मेरी सिफ़ारिशें',
        'nav.my_orders': 'मेरे ऑर्डर',
        'nav.doctor_appointments': 'डॉक्टर अपॉइंटमेंट्स',
        'nav.digital_prescriptions': 'डिजिटल पर्चे',
        'nav.consult_doctor': 'डॉक्टर परामर्श',
        'nav.dashboard': 'डैशबोर्ड',
        'nav.logout': 'लॉग आउट',
        'nav.login': 'लॉगिन',
        'nav.register': 'रजिस्टर',
        'nav.language': 'भाषा',
        'footer.copyright': '© 2026 AcuMeds. सभी अधिकार सुरक्षित।',
        'footer.disclaimer': 'अस्वीकरण: यह एक डेमो एप्लिकेशन है। चिकित्सा सलाह के लिए हमेशा स्वास्थ्य विशेषज्ञों से परामर्श करें।',
        'chatbot.title': 'AI सहायक',
        'chatbot.placeholder': 'इस पृष्ठ के बारे में कुछ भी पूछें...',
        'chatbot.send': 'भेजें',
        'chatbot.you': 'आप',
        'chatbot.bot': 'बॉट',
        'chatbot.no_response': 'कोई उत्तर नहीं मिला।',
        'chatbot.unavailable': 'AI सेवा अभी उपलब्ध नहीं है। कृपया फिर से प्रयास करें।',
        'title.login': 'लॉगिन',
        'title.register': 'रजिस्टर',
        'title.forgot_password': 'पासवर्ड भूल गए',
        'title.reset_password': 'पासवर्ड रीसेट',
        'title.home': 'होम',
        'title.dashboard': 'डैशबोर्ड',
        'auth.username_or_email': 'उपयोगकर्ता नाम या ईमेल',
        'auth.password': 'पासवर्ड',
        'auth.forgot_password': 'पासवर्ड भूल गए?',
        'auth.no_account': 'क्या आपके पास खाता नहीं है?',
        'auth.already_have_account': 'क्या आपके पास पहले से खाता है?',
        'auth.login_here': 'यहाँ लॉगिन करें',
        'auth.register_here': 'यहाँ रजिस्टर करें',
        'auth.demo_credentials': 'डेमो क्रेडेंशियल्स',
        'auth.email_address': 'ईमेल पता',
        'auth.create_account': 'खाता बनाएं',
        'auth.confirm_password': 'पासवर्ड की पुष्टि करें',
        'auth.password_hint': 'पासवर्ड कम से कम 8 अक्षर का होना चाहिए।',
        'auth.back_to_login': 'वापस लॉगिन पर जाएँ',
        'auth.enter_email': 'अपना ईमेल पता दर्ज करें',
        'auth.email_help': 'हम इस ईमेल पर पासवर्ड रीसेट लिंक भेजेंगे।',
        'auth.send_reset_link': 'रीसेट लिंक भेजें',
        'auth.new_password': 'नया पासवर्ड',
        'auth.confirm_new_password': 'नए पासवर्ड की पुष्टि करें',
        'auth.set_new_password': 'नया पासवर्ड सेट करें',
        'auth.username': 'उपयोगकर्ता नाम',
        'home.hero_title': 'AcuMeds',
        'home.hero_tagline': 'AI-संचालित दवा सुझाव, तेज़ होम डिलीवरी और आसान रीफ़िल - देखभाल जो आपके पास आए।',
        'home.primary_cta': 'डैशबोर्ड पर जाएँ',
        'home.secondary_cta': 'लॉगिन / रजिस्टर',
        'home.symptom_cta': 'लक्षण जाँचें',
        'home.quick_symptom_title': 'त्वरित लक्षण जाँच',
        'home.quick_symptom_body': 'अपने लक्षण लिखें और तुरंत सुझाई गई दवाइयाँ पाएं।',
        'home.ai_match': 'AI मेल: 75%',
        'home.feature_ai_title': 'AI सिफ़ारिशें',
        'home.feature_ai_body': 'लक्षण बताइए और कारण सहित तुरंत दवा सुझाव पाएं।',
        'home.feature_delivery_title': 'तेज़ डिलीवरी',
        'home.feature_delivery_body': 'ऑर्डर पुष्टिकरण और होम डिलीवरी 2-5 कार्य दिवस में।',
        'home.feature_refill_title': 'रीफ़िल सब्सक्रिप्शन',
        'home.feature_refill_body': 'अपनी ज़रूरी दवाओं को अपने नियंत्रण वाले शेड्यूल पर ऑटो-रीफ़िल करें।',
        'home.shopkeeper_title': 'क्या आप फ़ार्मेसी मालिक हैं?',
        'home.shopkeeper_body': 'AcuMeds से जुड़ें और अपना व्यवसाय बढ़ाएँ। कुछ ही मिनटों में ऑनलाइन दवाइयाँ बेचना शुरू करें।',
        'home.shopkeeper_cta': 'अपनी दुकान पंजीकृत करें',
        'home.welcome_banner': 'MediCare Pharmacy में आपका स्वागत है',
        'home.welcome_text': 'आपकी सभी चिकित्सा ज़रूरतों के लिए विश्वसनीय ऑनलाइन फ़ार्मेसी',
        'home.order_text': 'प्रिस्क्रिप्शन सत्यापन और तेज़ डिलीवरी के साथ ऑनलाइन दवाइयाँ ऑर्डर करें',
        'home.shop_now': 'अभी खरीदें',
        'home.ai_check': 'AI लक्षण जाँच',
        'home.secure_title': 'सुरक्षित और संरक्षित',
        'home.secure_body': 'सभी लेन-देन एन्क्रिप्टेड और सुरक्षित हैं। आपका डेटा सुरक्षित है।',
        'home.delivery_title': 'तेज़ डिलीवरी',
        'home.delivery_body': 'अपनी दवाइयाँ 5 दिनों के भीतर घर पर प्राप्त करें।',
        'home.ai_title': 'AI सिफ़ारिशें',
        'home.ai_body': 'अपने लक्षणों के आधार पर तुरंत दवा सुझाव पाएं।',
        'home.featured_medicines': 'विशेष दवाइयाँ',
        'home.view_details': 'विवरण देखें',
        'home.add_to_cart': 'कार्ट में जोड़ें',
        'home.out_of_stock': 'स्टॉक उपलब्ध नहीं',
        'home.requires_prescription': 'प्रिस्क्रिप्शन आवश्यक',
        'home.browse_all': 'सभी दवाइयाँ देखें',
        'dashboard.welcome': 'स्वागत है, {name}!',
        'dashboard.edit_profile': 'प्रोफ़ाइल संपादित करें',
        'dashboard.items_in_cart': 'कार्ट में आइटम',
        'dashboard.total_orders': 'कुल ऑर्डर',
        'dashboard.symptom_checks': 'लक्षण जाँच',
        'dashboard.ai_recommendations': 'AI सिफ़ारिशें',
        'dashboard.recent_orders': 'हाल के ऑर्डर',
        'dashboard.recent_symptom_checks': 'हाल की लक्षण जाँच',
        'dashboard.recent_recommendations': 'आपके लिए सुझाया गया',
        'dashboard.view': 'देखें',
        'dashboard.view_all': 'सभी देखें',
        'dashboard.order_id': 'ऑर्डर आईडी',
        'dashboard.date': 'तारीख',
        'dashboard.amount': 'राशि',
        'dashboard.status': 'स्थिति',
        'dashboard.symptoms': 'लक्षण',
        'dashboard.no_orders': 'अभी कोई ऑर्डर नहीं है।',
        'dashboard.no_recommendations': 'अभी कोई सिफ़ारिश नहीं है।',
        'dashboard.recommendation_empty': 'व्यक्तिगत सिफ़ारिशें पाने के लिए ऑर्डर करना शुरू करें!',
        'dashboard.loading': 'सिफ़ारिशें लोड हो रही हैं...',
        'dashboard.browse_medicines': 'दवाइयाँ देखें',
        'dashboard.try_now': 'अभी आज़माएँ',
        'messages.language_changed': 'भाषा {language} में बदल दी गई है।',
        'messages.login_successful': 'लॉगिन सफल रहा!',
        'messages.account_created': 'खाता सफलतापूर्वक बन गया!',
        'messages.logged_out': 'आप लॉग आउट हो गए हैं',
        'messages.invalid_credentials': 'अमान्य उपयोगकर्ता नाम या पासवर्ड',
        'messages.account_deactivated': 'आपका खाता निष्क्रिय कर दिया गया है। कृपया सहायता से संपर्क करें।',
        'messages.all_fields_required': 'सभी फ़ील्ड आवश्यक हैं',
        'messages.passwords_do_not_match': 'पासवर्ड मेल नहीं खाते',
        'messages.username_exists': 'उपयोगकर्ता नाम पहले से मौजूद है',
        'messages.email_exists': 'ईमेल पहले से पंजीकृत है',
        'messages.reset_link_sent': 'पासवर्ड रीसेट लिंक आपके ईमेल पर भेज दिया गया है',
        'messages.reset_link_maybe_sent': 'यदि उस ईमेल वाला खाता मौजूद है, तो रीसेट लिंक भेजा जाएगा',
        'messages.enter_question_first': 'कृपया पहले एक प्रश्न लिखें।',
        'messages.start_shopping': 'खरीदारी शुरू करें!',
        'messages.try_ai_checker': 'हमारे AI लक्षण जाँचकर्ता को आज़माएँ!',
        'messages.browse_medicines': 'दवाइयाँ देखें',
        'messages.no_orders_yet': 'अभी कोई ऑर्डर नहीं है।',
        'messages.no_recommendations_yet': 'अभी कोई सिफ़ारिश नहीं है।',
        'messages.start_orders_for_recommendations': 'व्यक्तिगत सिफ़ारिशें पाने के लिए ऑर्डर करना शुरू करें!',
        'messages.loading_recommendations': 'सिफ़ारिशें लोड हो रही हैं...',
        'messages.error_loading_recommendations': 'सिफ़ारिशें लोड करने में त्रुटि',
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
    """Return a supported language code or the default language."""
    if language_code in SUPPORTED_LANGUAGES:
        return language_code
    return DEFAULT_LANGUAGE


def get_current_language():
    """Determine the active language for the current request."""
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
    """Persist the selected language in the session."""
    session['language'] = normalize_language(language_code)
    return session['language']


def get_language_label(language_code=None):
    """Return the human readable label for a language code."""
    normalized = normalize_language(language_code or get_current_language())
    return SUPPORTED_LANGUAGES[normalized]


def get_language_options():
    """Return language options for template dropdowns."""
    return [(code, label) for code, label in SUPPORTED_LANGUAGES.items()]


def translate(key, **kwargs):
    """Translate a UI key using the active language."""
    language_code = get_current_language()
    language_catalog = TRANSLATIONS.get(language_code, TRANSLATIONS[DEFAULT_LANGUAGE])
    text = language_catalog.get(key, TRANSLATIONS[DEFAULT_LANGUAGE].get(key, key))
    if kwargs:
        return text.format(**kwargs)
    return text


def translate_message(message, **kwargs):
    """Translate a flashed message if a matching entry exists."""
    language_code = get_current_language()
    translated = MESSAGE_TRANSLATIONS.get(language_code, {}).get(message, message)
    if kwargs:
        return translated.format(**kwargs)
    return translated