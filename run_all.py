#!/usr/bin/env python
"""
AcuMeds All-in-One Multi-System Runner
Launches and monitors all 5 systems simultaneously:
1. Pharmacy / Customer Portal  -> http://localhost:5000
2. Shopkeeper Portal           -> http://localhost:5001
3. Admin Portal                -> http://localhost:5002
4. Delivery Portal             -> http://localhost:5003
5. Doctor Portal               -> http://localhost:5004
"""

import os
import sys
import time
import socket
import signal
import threading
import subprocess
import webbrowser
import argparse

# ANSI color codes for rich terminal output
COLORS = {
    "CUSTOMER": "\033[92m",    # Green
    "SHOPKEEPER": "\033[93m",  # Yellow
    "ADMIN": "\033[96m",       # Cyan
    "DELIVERY": "\033[95m",    # Magenta
    "DOCTOR": "\033[94m",      # Blue
    "SYSTEM": "\033[97m\033[1m", # Bold White
    "ERROR": "\033[91m\033[1m",  # Bold Red
    "RESET": "\033[0m",
}

# Fix Windows ANSI coloring support
if sys.platform == "win32":
    os.system("color")

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

SERVICES = [
    {
        "key": "CUSTOMER",
        "name": "Customer / Pharmacy",
        "dir": "pharmacy_system",
        "script": "run.py",
        "port": 5000,
        "url": "http://localhost:5000",
        "creds": "Public / Register or Login",
    },
    {
        "key": "SHOPKEEPER",
        "name": "Shopkeeper Portal",
        "dir": "shopkeeper_system",
        "script": "run.py",
        "port": 5001,
        "url": "http://localhost:5001",
        "creds": "shopkeeper1 / shopkeeper123",
    },
    {
        "key": "ADMIN",
        "name": "Admin Portal",
        "dir": "admin_system",
        "script": "run.py",
        "port": 5002,
        "url": "http://localhost:5002",
        "creds": "admin / admin123",
    },
    {
        "key": "DELIVERY",
        "name": "Delivery Portal",
        "dir": "delivery_system",
        "script": "run.py",
        "port": 5003,
        "url": "http://localhost:5003",
        "creds": "delivery1 / delivery123",
    },
    {
        "key": "DOCTOR",
        "name": "Doctor Portal",
        "dir": "doctor_system",
        "script": "run.py",
        "port": 5004,
        "url": "http://localhost:5004",
        "creds": "doctor1 / doctor123",
    },
]

running_processes = []
stop_requested = threading.Event()


def is_port_in_use(port):
    """Check if a port is actively bound."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) == 0


def get_python_executable():
    """Detect python executable, preferring virtual environment."""
    venv_py = os.path.join(BASE_DIR, ".venv", "Scripts", "python.exe")
    if os.path.exists(venv_py):
        return venv_py
    venv_py_unix = os.path.join(BASE_DIR, ".venv", "bin", "python")
    if os.path.exists(venv_py_unix):
        return venv_py_unix
    return sys.executable


def stream_logs(process, key):
    """Stream subprocess logs with a colorized tag."""
    color = COLORS.get(key, "")
    reset = COLORS["RESET"]
    prefix = f"{color}[{key:10s}]{reset} "
    
    try:
        for line in iter(process.stdout.readline, ""):
            if stop_requested.is_set():
                break
            if line:
                sys.stdout.write(f"{prefix}{line}")
                sys.stdout.flush()
    except Exception:
        pass


def kill_all():
    """Terminate all spawned processes gracefully and forcefully if needed."""
    if stop_requested.is_set():
        return
    stop_requested.set()
    
    print(f"\n{COLORS['SYSTEM']}[SYSTEM] Shutting down all services...{COLORS['RESET']}")
    for proc, svc in running_processes:
        if proc.poll() is None:
            try:
                proc.terminate()
            except Exception:
                pass
    
    time.sleep(1)
    for proc, svc in running_processes:
        if proc.poll() is None:
            try:
                proc.kill()
            except Exception:
                pass
    print(f"{COLORS['SYSTEM']}[SYSTEM] All 5 services stopped successfully.{COLORS['RESET']}")


def main():
    parser = argparse.ArgumentParser(description="Run all 5 AcuMeds systems simultaneously.")
    parser.add_argument("--no-browser", action="store_true", help="Do not open browser tabs automatically")
    parser.add_argument("--hub", action="store_true", help="Open Live Project Hub dashboard instead of 5 separate tabs")
    args = parser.parse_args()

    python_exe = get_python_executable()
    print("=" * 72)
    print(f"{COLORS['SYSTEM']}   ACUMEDS UNIFIED RUNNER - 5 SERVICES SIMULTANEOUS LAUNCH{COLORS['RESET']}")
    print("=" * 72)
    print(f"Python: {python_exe}")
    print(f"Root:   {BASE_DIR}")
    print("-" * 72)
    
    # Check database initialization
    db_file = os.path.join(BASE_DIR, "admin_system", "database", "pharmacy.db")
    if not os.path.exists(db_file):
        print(f"{COLORS['SYSTEM']}[SYSTEM] Initializing shared database...{COLORS['RESET']}")
        init_script = os.path.join(BASE_DIR, "init_doctor_db.py")
        if os.path.exists(init_script):
            subprocess.run([python_exe, init_script], cwd=BASE_DIR)

    # Check port conflicts
    for svc in SERVICES:
        if is_port_in_use(svc["port"]):
            print(f"{COLORS['ERROR']}[WARNING] Port {svc['port']} ({svc['name']}) is already in use!{COLORS['RESET']}")
            print(f"         If another instance is running, please close it first.")

    # Start all services
    print(f"\n{COLORS['SYSTEM']}[SYSTEM] Launching all 5 services simultaneously...{COLORS['RESET']}\n")
    
    for svc in SERVICES:
        svc_dir = os.path.join(BASE_DIR, svc["dir"])
        run_file = os.path.join(svc_dir, svc["script"])
        
        if not os.path.exists(run_file):
            print(f"{COLORS['ERROR']}[ERROR] Script not found: {run_file}{COLORS['RESET']}")
            continue
        
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        
        proc = subprocess.Popen(
            [python_exe, svc["script"]],
            cwd=svc_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            env=env
        )
        
        running_processes.append((proc, svc))
        
        # Start log reader thread
        t = threading.Thread(target=stream_logs, args=(proc, svc["key"]), daemon=True)
        t.start()
        
        print(f"  {COLORS[svc['key']]}●{COLORS['RESET']} {svc['name']:<24} -> {svc['url']:<24} (Credentials: {svc['creds']})")

    print("\n" + "=" * 72)
    print(f"{COLORS['SYSTEM']}All services are running! Press Ctrl+C at any time to stop all.{COLORS['RESET']}")
    print("=" * 72 + "\n")

    # Open browser if requested
    if not args.no_browser:
        time.sleep(2)
        if args.hub:
            hub_path = os.path.join(BASE_DIR, "AcuMeds_Live_Hub.html")
            if os.path.exists(hub_path):
                webbrowser.open(f"file:///{hub_path}")
        else:
            # Open the portals
            for svc in SERVICES:
                try:
                    webbrowser.open(svc["url"])
                except Exception:
                    pass

    # Wait for processes or interrupt
    def handle_sig(sig, frame):
        kill_all()
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_sig)
    signal.signal(signal.SIGTERM, handle_sig)

    try:
        while True:
            time.sleep(1)
            # Check if any process died unexpectedly
            for proc, svc in running_processes:
                ret = proc.poll()
                if ret is not None and not stop_requested.is_set():
                    print(f"{COLORS['ERROR']}[SYSTEM] Process {svc['name']} exited with code {ret}{COLORS['RESET']}")
    except KeyboardInterrupt:
        kill_all()


if __name__ == "__main__":
    main()
