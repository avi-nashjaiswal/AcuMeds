#!/usr/bin/env python
"""
AcuMeds Production Multi-Service WSGI Server
Runs all 5 AcuMeds portals concurrently using production-grade WSGI (Waitress)
with complete process-level isolation and graceful lifecycle management.

Services:
  1. Pharmacy / Customer Portal  : Port $PORT / 5000 (Primary public entrypoint)
  2. Shopkeeper Portal           : Port $PORT_SHOPKEEPER / 5001
  3. Admin Portal                : Port $PORT_ADMIN / 5002
  4. Delivery Portal             : Port $PORT_DELIVERY / 5003
  5. Doctor Telehealth Portal    : Port $PORT_DOCTOR / 5004
"""

import os
import sys
import ast
import time
import signal
import socket
import threading
import subprocess
from datetime import datetime

# Polyfill ast attributes removed in Python 3.14+ for legacy library compatibility
if sys.version_info >= (3, 14):
    for _ast_attr in ('Str', 'Num', 'Bytes', 'NameConstant', 'Ellipsis'):
        if not hasattr(ast, _ast_attr):
            setattr(ast, _ast_attr, getattr(ast, 'Constant', object))

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '.env.production'))
    load_dotenv(os.path.join(os.path.dirname(__file__), '.env.local'))
    load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
except ImportError:
    pass

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')


def is_port_bound(port, host="127.0.0.1"):
    """Check if a port is actively open and responding."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0


def ensure_database():
    """Verify and initialize shared database and schema migrations."""
    db_path = os.path.join(BASE_DIR, "admin_system", "database", "pharmacy.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    # 1. Run migrations if available
    migrate_script = os.path.join(BASE_DIR, "migrate_db.py")
    if os.path.exists(migrate_script):
        try:
            res = subprocess.run([sys.executable, migrate_script], cwd=BASE_DIR, capture_output=True, text=True)
            if res.returncode == 0:
                print("[+] Database migration check completed.")
            else:
                print(f"[!] Migration check notice: {res.stdout.strip() or res.stderr.strip()}")
        except Exception as e:
            print(f"[!] Migration check warning: {e}")

    # 2. Run doctor db init
    init_doc_script = os.path.join(BASE_DIR, "init_doctor_db.py")
    if os.path.exists(init_doc_script):
        try:
            res = subprocess.run([sys.executable, init_doc_script], cwd=BASE_DIR, capture_output=True, text=True)
            if res.returncode == 0:
                print("[+] Doctor portal database check completed.")
            else:
                print(f"[!] Doctor init check notice: {res.stdout.strip() or res.stderr.strip()}")
        except Exception as e:
            print(f"[!] Doctor init check warning: {e}")


def stream_process_logs(proc, name):
    """Stream process stdout/stderr cleanly."""
    try:
        for line in iter(proc.stdout.readline, ''):
            if line:
                if "DeprecationWarning" in line:
                    continue
                sys.stdout.write(f"[{name}] {line}")
                sys.stdout.flush()
    except Exception:
        pass


def main():
    print("=" * 72)
    print("   ACUMEDS - PRODUCTION MULTI-SERVICE WSGI SERVER")
    print("=" * 72)
    print(f"Timestamp : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Root Dir  : {BASE_DIR}")
    print(f"Python    : {sys.version.split()[0]}")
    print("-" * 72)

    # 1. Run database initialization and migrations
    ensure_database()
    print("-" * 72)

    # 2. Define service registry
    # On Render, the primary public entrypoint listens on Render's $PORT (e.g. 10000)
    primary_port = int(os.getenv("PORT", os.getenv("PORT_PHARMACY", 5000)))

    services = [
        {"name": "Customer / Pharmacy", "dir": "pharmacy_system",   "port": primary_port},
        {"name": "Shopkeeper Portal",   "dir": "shopkeeper_system", "port": int(os.getenv("PORT_SHOPKEEPER", 5001))},
        {"name": "Admin Panel",         "dir": "admin_system",      "port": int(os.getenv("PORT_ADMIN", 5002))},
        {"name": "Delivery Portal",     "dir": "delivery_system",   "port": int(os.getenv("PORT_DELIVERY", 5003))},
        {"name": "Doctor Telehealth",   "dir": "doctor_system",     "port": int(os.getenv("PORT_DOCTOR", 5004))},
    ]

    host = os.getenv("HOST", "0.0.0.0")
    threads_per_service = int(os.getenv("WSGI_THREADS", "6"))
    active_procs = []

    # 3. Launch each WSGI worker in an isolated subprocess
    print("Starting production WSGI workers with process-level isolation:")
    for svc in services:
        sdir = os.path.join(BASE_DIR, svc["dir"])
        port = svc["port"]
        name = svc["name"]

        worker_script = f"""
import sys, os, ast
if sys.version_info >= (3, 14):
    for _a in ('Str', 'Num', 'Bytes', 'NameConstant', 'Ellipsis'):
        if not hasattr(ast, _a):
            setattr(ast, _a, getattr(ast, 'Constant', object))
sys.path.insert(0, os.path.abspath(r'{sdir}'))
try:
    from waitress import serve
    from app import create_app
    app = create_app()
    serve(app, host='{host}', port={port}, threads={threads_per_service}, _quiet=True)
except Exception as e:
    import traceback
    traceback.print_exc()
    sys.exit(1)
"""
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"

        try:
            proc = subprocess.Popen(
                [sys.executable, "-c", worker_script],
                cwd=sdir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                env=env
            )
            active_procs.append((proc, svc))
            print(f"  [+] {name:<26} starting on http://{host}:{port} ({threads_per_service} WSGI threads)")
            sys.stdout.flush()

            # Start background log streamer thread
            log_t = threading.Thread(target=stream_process_logs, args=(proc, name), daemon=True)
            log_t.start()
        except Exception as e:
            print(f"  [X] Failed to launch {name}: {e}")

    print("-" * 72)
    print("All 5 WSGI services are active and serving production traffic:")
    for svc in services:
        print(f"  * {svc['name']:<24} -> http://localhost:{svc['port']}")
    print("=" * 72)
    print("Press Ctrl+C to terminate production server.\n")
    sys.stdout.flush()

    # Graceful shutdown handler
    def handle_exit(signum, frame):
        print("\n[+] Graceful shutdown initiated. Terminating WSGI workers...")
        for p, s in active_procs:
            if p.poll() is None:
                try:
                    p.terminate()
                except Exception:
                    pass
        time.sleep(1)
        for p, s in active_procs:
            if p.poll() is None:
                try:
                    p.kill()
                except Exception:
                    pass
        print("[+] All WSGI workers stopped.")
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    # Monitor loop
    try:
        while True:
            time.sleep(2)
            for p, svc in active_procs:
                ret = p.poll()
                if ret is not None:
                    print(f"[!] Warning: {svc['name']} (Port {svc['port']}) exited unexpectedly with code {ret}")
    except KeyboardInterrupt:
        handle_exit(None, None)


if __name__ == "__main__":
    main()
