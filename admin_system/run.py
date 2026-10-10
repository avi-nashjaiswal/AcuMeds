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

from app import create_app

if __name__ == '__main__':
    app = create_app()
    print("\n" + "="*60)
    print("[+] ADMIN PORTAL STARTING...")
    print("="*60)
    print("URL: http://localhost:5002")
    print("Login: admin / admin123")
    print("="*60 + "\n")
    app.run(debug=True, port=5002, host='localhost')
