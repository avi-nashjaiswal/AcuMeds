#!/usr/bin/env python
"""
Admin Portal - Main Entry Point
Runs on Port 5002
"""
import warnings
try:
    from requests.packages.urllib3.exceptions import RequestsDependencyWarning
    warnings.filterwarnings("ignore", category=RequestsDependencyWarning)
except Exception:
    pass

import os
from app import create_app

# Create Flask app instance for WSGI compatibility (Gunicorn/Waitress/uWSGI)
app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5002))
    host = os.getenv('HOST', '0.0.0.0')
    debug = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    
    print("\n" + "="*60)
    print("[+] ADMIN PORTAL STARTING...")
    print("="*60)
    print(f"URL: http://{host}:{port}")
    print("Login: admin / admin123")
    print("="*60 + "\n")
    app.run(debug=debug, port=port, host=host)

