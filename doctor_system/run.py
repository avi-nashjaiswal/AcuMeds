#!/usr/bin/env python
"""
AcuMeds Doctor Portal - Main Entry Point
Runs on Port 5004
"""
import os
import sys
import warnings

try:
    from requests.packages.urllib3.exceptions import RequestsDependencyWarning
    warnings.filterwarnings("ignore", category=RequestsDependencyWarning)
except Exception:
    pass

from app import create_app

app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5004))
    host = os.getenv('HOST', '0.0.0.0')
    debug = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    
    print("\n" + "="*60)
    print("[+] ACUMEDS DOCTOR PORTAL STARTING...")
    print("="*60)
    print(f"URL: http://{host}:{port}")
    print("Login: doctor1 / doctor123")
    print("="*60 + "\n")
    app.run(debug=debug, host=host, port=port)

