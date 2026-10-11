#!/usr/bin/env python
"""
AcuMeds Production Multi-Service WSGI Server
Runs all 5 AcuMeds portals concurrently using production-grade WSGI (Waitress).
Works on Windows, Linux, macOS, and inside Docker containers.

Services:
  1. Pharmacy / Customer Portal  : Port 5000 (http://0.0.0.0:5000)
  2. Shopkeeper Portal           : Port 5001 (http://0.0.0.0:5001)
  3. Admin Portal                : Port 5002 (http://0.0.0.0:5002)
  4. Delivery Portal             : Port 5003 (http://0.0.0.0:5003)
  5. Doctor Telehealth Portal    : Port 5004 (http://0.0.0.0:5004)
"""

import os
import sys
import time
import signal
import threading
import socket
from datetime import datetime

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '.env.production'))
    load_dotenv(os.path.join(os.path.dirname(__file__), '.env.local'))
    load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
except ImportError:
    pass

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Ensure Python path includes root
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


def is_port_bound(port, host="127.0.0.1"):
    """Check if a port is actively open and responding."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0


def ensure_database():
    """Verify and initialize shared database and schema migrations."""
    db_path = os.path.join(BASE_DIR, "admin_system", "database", "pharmacy.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Run migrations if available
    migrate_script = os.path.join(BASE_DIR, "migrate_db.py")
    if os.path.exists(migrate_script):
        try:
            import migrate_db
            print("[+] Database migration check completed.")
        except Exception as e:
            print(f"[!] Migration check warning: {e}")

    # Run doctor db init
    init_doc_script = os.path.join(BASE_DIR, "init_doctor_db.py")
    if os.path.exists(init_doc_script):
        try:
            import init_doctor_db
            print("[+] Doctor portal database check completed.")
        except Exception as e:
            print(f"[!] Doctor init check warning: {e}")


if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')


def run_wsgi_service(name, app_module_path, port, host="0.0.0.0", threads=6):
    """Run a single Flask app inside a Waitress WSGI server worker."""
    sys.path.insert(0, os.path.join(BASE_DIR, app_module_path))
    try:
        from waitress import serve
        from app import create_app
        app = create_app()
        print(f"  [+] {name:<26} starting on http://{host}:{port} ({threads} WSGI threads)")
        serve(app, host=host, port=port, threads=threads, _quiet=True)
    except Exception as e:
        print(f"  [X] Error in {name} (Port {port}): {e}")



def main():
    print("=" * 72)
    print("   ACUMEDS - PRODUCTION MULTI-SERVICE WSGI SERVER")
    print("=" * 72)
    print(f"Timestamp : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Root Dir  : {BASE_DIR}")
    print(f"Python    : {sys.version.split()[0]}")
    print("-" * 72)

    # 1. Database check
    ensure_database()
    print("-" * 72)

    # 2. Define service registry
    services = [
        {"name": "Customer / Pharmacy", "dir": "pharmacy_system",   "port": int(os.getenv("PORT", os.getenv("PORT_PHARMACY", 5000)))},
        {"name": "Shopkeeper Portal",   "dir": "shopkeeper_system", "port": int(os.getenv("PORT_SHOPKEEPER", 5001))},
        {"name": "Admin Panel",         "dir": "admin_system",      "port": int(os.getenv("PORT_ADMIN", 5002))},
        {"name": "Delivery Portal",     "dir": "delivery_system",   "port": int(os.getenv("PORT_DELIVERY", 5003))},
        {"name": "Doctor Telehealth",   "dir": "doctor_system",     "port": int(os.getenv("PORT_DOCTOR", 5004))},
    ]

    # Check port conflicts
    for svc in services:
        if is_port_bound(svc["port"]):
            print(f"[!] Warning: Port {svc['port']} ({svc['name']}) is already bound by another process!")

    # 3. Start WSGI threads
    threads = []
    host = os.getenv("HOST", "0.0.0.0")

    for svc in services:
        t = threading.Thread(
            target=run_wsgi_service,
            args=(svc["name"], svc["dir"], svc["port"], host),
            daemon=True,
            name=f"wsgi-{svc['dir']}"
        )
        t.start()
        threads.append(t)
        time.sleep(0.3)

    print("-" * 72)
    print("All 5 WSGI services are live and serving production traffic:")
    for svc in services:
        print(f"  * {svc['name']:<24} -> http://localhost:{svc['port']}")
    print("=" * 72)
    print("Press Ctrl+C to terminate production server.\n")

    def handle_exit(signum, frame):
        print("\n[+] Graceful shutdown initiated. Stopping WSGI workers...")
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    # Keep alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        handle_exit(None, None)


if __name__ == "__main__":
    main()
