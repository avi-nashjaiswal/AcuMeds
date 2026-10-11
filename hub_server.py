#!/usr/bin/env python
"""
AcuMeds Live Project Hub Server
Standalone production service for the central dashboard linking all 5 independent AcuMeds portals.
Runs on Render with its own unique public URL (e.g., https://acumed-hub.onrender.com).
"""

import os
import sys
import time
import ast
from flask import Flask, jsonify, make_response, send_file, render_template_string

# Polyfill ast attributes removed in Python 3.14+ for legacy library compatibility
if sys.version_info >= (3, 14):
    for _ast_attr in ('Str', 'Num', 'Bytes', 'NameConstant', 'Ellipsis'):
        if not hasattr(ast, _ast_attr):
            setattr(ast, _ast_attr, getattr(ast, 'Constant', object))

# Load environment variables if dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '.env.production'))
    load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
except ImportError:
    pass

app = Flask(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
HUB_HTML_PATH = os.path.join(BASE_DIR, 'AcuMeds_Live_Hub.html')

def get_portal_urls():
    """Retrieve configured portal URLs with intelligent cloud fallbacks."""
    return {
        "customer": os.getenv("URL_CUSTOMER", "https://acumed-customer.onrender.com").rstrip('/'),
        "shopkeeper": os.getenv("URL_SHOPKEEPER", "https://acumed-shopkeeper.onrender.com").rstrip('/'),
        "admin": os.getenv("URL_ADMIN", "https://acumed-admin.onrender.com").rstrip('/'),
        "doctor": os.getenv("URL_DOCTOR", "https://acumed-doctor.onrender.com").rstrip('/'),
        "delivery": os.getenv("URL_DELIVERY", "https://acumed-delivery.onrender.com").rstrip('/'),
    }


@app.after_request
def add_cors_headers(response):
    """Enable CORS headers for cross-domain dashboard communication."""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,OPTIONS'
    return response


@app.route('/health')
def health_check():
    """Health check endpoint for Render service monitoring."""
    return jsonify({
        "status": "ok",
        "service": "live_hub",
        "timestamp": int(time.time()),
        "portals": get_portal_urls()
    }), 200


@app.route('/api/config')
def portal_config():
    """API endpoint providing current live portal URLs to frontends."""
    return jsonify(get_portal_urls()), 200


@app.route('/')
@app.route('/hub')
def serve_hub():
    """Serve AcuMeds Live Project Hub dashboard with dynamic portal URLs injected."""
    if not os.path.exists(HUB_HTML_PATH):
        return "AcuMeds_Live_Hub.html not found", 404

    with open(HUB_HTML_PATH, 'r', encoding='utf-8') as f:
        html_content = f.read()

    portals = get_portal_urls()
    
    # Inject client-side configuration into HTML
    injection_script = f"""
    <script>
      window.ACUMEDS_PORTALS = {jsonify(portals).get_data(as_text=True)};
      (function() {{
        function applyUrls() {{
          if (window.ACUMEDS_PORTALS) {{
            var c = document.getElementById('link-user');
            var s = document.getElementById('link-shopkeeper');
            var a = document.getElementById('link-admin');
            var d = document.getElementById('link-doctor');
            var dl = document.getElementById('link-delivery');
            if (c) c.href = window.ACUMEDS_PORTALS.customer || '/';
            if (s) s.href = window.ACUMEDS_PORTALS.shopkeeper || '/shopkeeper/';
            if (a) a.href = window.ACUMEDS_PORTALS.admin || '/admin/';
            if (d) d.href = window.ACUMEDS_PORTALS.doctor || '/doctor/';
            if (dl) dl.href = window.ACUMEDS_PORTALS.delivery || '/delivery/';
          }}
        }}
        if (document.readyState === 'loading') {{
          document.addEventListener('DOMContentLoaded', applyUrls);
        }} else {{
          applyUrls();
        }}
      }})();
    </script>
    """

    if "</body>" in html_content:
        html_content = html_content.replace("</body>", f"{injection_script}\n</body>")
    else:
        html_content += injection_script

    response = make_response(html_content)
    response.headers['Content-Type'] = 'text/html; charset=utf-8'
    return response


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5005))
    host = os.getenv('HOST', '0.0.0.0')
    debug = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')

    print("=" * 64)
    print("   ACUMEDS - LIVE PROJECT HUB PRODUCTION SERVER")
    print("=" * 64)
    print(f"URL: http://{host}:{port}")
    print("Portals configured:")
    for k, v in get_portal_urls().items():
        print(f"  * {k:<12}: {v}")
    print("=" * 64)

    if not debug:
        try:
            from waitress import serve
            serve(app, host=host, port=port, threads=int(os.getenv('WSGI_THREADS', '6')), _quiet=True)
        except ImportError:
            app.run(debug=debug, host=host, port=port)
    else:
        app.run(debug=debug, host=host, port=port)
