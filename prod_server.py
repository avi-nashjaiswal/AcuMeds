#!/usr/bin/env python
"""
AcuMeds Production Multi-Service WSGI Server & Unified Cloud Gateway
Runs all 5 AcuMeds portals with isolated WSGI workers and exposes a unified
subpath reverse proxy gateway on port $PORT (Render default 10000).

Unified Public Endpoints:
  - /             -> Customer Storefront & E-Pharmacy (Internal Port 5000/5010)
  - /hub          -> AcuMeds Live Project Hub (Interactive 1-Click Access)
  - /shopkeeper/  -> Shopkeeper Inventory & Orders Portal (Internal Port 5001)
  - /admin/       -> Super Admin & Management Console (Internal Port 5002)
  - /delivery/    -> Delivery Agent Dispatch Portal (Internal Port 5003)
  - /doctor/      -> Doctor Telehealth & Digital Rx Portal (Internal Port 5004)
"""

import os
import sys
import ast
import time
import signal
import socket
import threading
import subprocess
import re
import urllib.request
import urllib.error
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


class UnifiedGateway:
    """WSGI Reverse Proxy Gateway routing all 5 portals through a single public port."""
    def __init__(self, routes, customer_port=5000):
        self.routes = routes  # {"/shopkeeper": 5001, "/admin": 5002, "/delivery": 5003, "/doctor": 5004}
        self.customer_port = customer_port
        self.hub_html_path = os.path.join(BASE_DIR, 'AcuMeds_Live_Hub.html')

    def __call__(self, environ, start_response):
        path = environ.get('PATH_INFO', '/')
        method = environ.get('REQUEST_METHOD', 'GET')
        query = environ.get('QUERY_STRING', '')

        # 1. Serve Live Hub Dashboard
        if path in ('/hub', '/hub/'):
            try:
                with open(self.hub_html_path, 'rb') as f:
                    content = f.read()
                start_response('200 OK', [
                    ('Content-Type', 'text/html; charset=utf-8'),
                    ('Content-Length', str(len(content))),
                    ('Cache-Control', 'no-cache')
                ])
                return [content]
            except Exception as e:
                err = f"Live Hub error: {e}".encode()
                start_response('500 Internal Server Error', [('Content-Type', 'text/plain'), ('Content-Length', str(len(err)))])
                return [err]

        # 2. Redirect exact prefix without trailing slash (e.g. /shopkeeper -> /shopkeeper/)
        for prefix in self.routes.keys():
            if path == prefix:
                target_url = f"{prefix}/" + (f"?{query}" if query else "")
                start_response('302 Found', [('Location', target_url), ('Content-Length', '0')])
                return [b'']

        # 3. Match route prefix
        target_port = self.customer_port
        prefix = ""
        for p, port in self.routes.items():
            if path.startswith(p + '/'):
                target_port = port
                prefix = p
                break

        # 4. Determine target path
        if prefix:
            target_path = path[len(prefix):]
            if not target_path or not target_path.startswith('/'):
                target_path = '/' + target_path
        else:
            target_path = path

        url = f"http://127.0.0.1:{target_port}{target_path}"
        if query:
            url += f"?{query}"

        # 5. Build forwarded headers
        headers = {}
        for k, v in environ.items():
            if k.startswith('HTTP_'):
                h_name = k[5:].replace('_', '-').title()
                if h_name not in ('Host', 'Content-Length'):
                    headers[h_name] = v
            elif k in ('CONTENT_TYPE', 'CONTENT_LENGTH') and v:
                h_name = k.replace('_', '-').title()
                headers[h_name] = v

        client_host = environ.get('HTTP_X_FORWARDED_HOST') or environ.get('HTTP_HOST') or 'localhost:10000'
        client_proto = environ.get('HTTP_X_FORWARDED_PROTO') or environ.get('wsgi.url_scheme', 'https')
        client_ip = environ.get('HTTP_X_FORWARDED_FOR') or environ.get('REMOTE_ADDR', '127.0.0.1')

        headers['Host'] = f"127.0.0.1:{target_port}"
        headers['X-Forwarded-Host'] = client_host
        headers['X-Forwarded-Proto'] = client_proto
        headers['X-Forwarded-For'] = client_ip
        if prefix:
            headers['X-Forwarded-Prefix'] = prefix

        # 6. Read request body if present
        body = None
        if method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            try:
                cl = int(environ.get('CONTENT_LENGTH', 0))
                if cl > 0:
                    body = environ['wsgi.input'].read(cl)
            except Exception:
                pass

        # 7. Proxy request to internal backend
        class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, hdrs, newurl):
                return None

        opener = urllib.request.build_opener(NoRedirectHandler)

        try:
            req = urllib.request.Request(url, data=body, headers=headers, method=method)
            try:
                resp = opener.open(req, timeout=30)
                status = f"{resp.status} {resp.reason}"
                resp_headers = resp.getheaders()
                resp_body = resp.read()
            except urllib.error.HTTPError as e:
                status = f"{e.code} {e.reason}"
                resp_headers = e.headers.items()
                resp_body = e.read()

            out_headers = []
            is_html = False
            for k, v in resp_headers:
                lk = k.lower()
                if lk in ('transfer-encoding', 'connection', 'content-length'):
                    continue
                if lk == 'content-type' and 'text/html' in v.lower():
                    is_html = True
                # Rewrite Location header for redirects from sub-portals
                if lk == 'location' and prefix:
                    if v.startswith('/') and not v.startswith(prefix + '/') and v != prefix:
                        v = f"{prefix}{v}"
                    elif v.startswith(f"http://127.0.0.1:{target_port}"):
                        rel = v[len(f"http://127.0.0.1:{target_port}"):]
                        v = f"{prefix}{rel}" if rel.startswith('/') else f"{prefix}/{rel}"
                out_headers.append((k, v))

            # Rewrite HTML links for sub-portals so navigation stays in subpath
            if is_html and prefix:
                try:
                    html_text = resp_body.decode('utf-8', errors='replace')
                    def _rewrite_attr(m):
                        attr = m.group(1)
                        val = m.group(2)
                        if val.startswith('/') and not val.startswith(prefix + '/') and val != prefix:
                            return f'{attr}="{prefix}{val}"'
                        return m.group(0)

                    html_text = re.sub(r'\b(href|action|src)=["\'](/[^"\']*)["\']', _rewrite_attr, html_text)
                    resp_body = html_text.encode('utf-8')
                except Exception:
                    pass

            out_headers.append(('Content-Length', str(len(resp_body))))
            start_response(status, out_headers)
            return [resp_body]

        except Exception as err:
            err_html = f"""<!doctype html>
<html>
<head><title>AcuMeds Portal Initializing</title></head>
<body style="font-family: system-ui, sans-serif; background: #0f172a; color: #f8fafc; display: flex; align-items: center; justify-content: center; height: 90vh;">
  <div style="text-align: center; max-width: 520px; padding: 32px; border-radius: 20px; background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.12);">
    <h2 style="color: #2dd4bf; margin-top: 0;">Portal Initializing</h2>
    <p style="color: #94a3b8; line-height: 1.6;">The requested service is warming up internal WSGI workers. Please refresh in a moment.</p>
    <a href="{path}" style="display: inline-block; margin-top: 14px; padding: 12px 28px; background: #0f766e; color: white; border-radius: 10px; text-decoration: none; font-weight: bold;">Refresh Page</a>
  </div>
</body>
</html>""".encode('utf-8')
            start_response('503 Service Unavailable', [('Content-Type', 'text/html; charset=utf-8'), ('Content-Length', str(len(err_html)))])
            return [err_html]


def main():
    print("=" * 72)
    print("   ACUMEDS - PRODUCTION UNIFIED GATEWAY & MULTI-PORTAL SERVER")
    print("=" * 72)
    print(f"Timestamp : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Root Dir  : {BASE_DIR}")
    print(f"Python    : {sys.version.split()[0]}")
    print("-" * 72)

    # 1. Run database initialization and migrations
    ensure_database()
    print("-" * 72)

    # 2. Determine public gateway port vs internal ports
    # Render binds incoming public traffic to $PORT (usually 10000)
    gateway_port = int(os.getenv("PORT", 10000))

    # Avoid port collision with customer internal port
    internal_customer_port = 5010 if gateway_port == 5000 else 5000
    internal_shopkeeper_port = 5001
    internal_admin_port = 5002
    internal_delivery_port = 5003
    internal_doctor_port = 5004

    services = [
        {"name": "Customer / Pharmacy", "dir": "pharmacy_system",   "port": internal_customer_port},
        {"name": "Shopkeeper Portal",   "dir": "shopkeeper_system", "port": internal_shopkeeper_port},
        {"name": "Admin Panel",         "dir": "admin_system",      "port": internal_admin_port},
        {"name": "Delivery Portal",     "dir": "delivery_system",   "port": internal_delivery_port},
        {"name": "Doctor Telehealth",   "dir": "doctor_system",     "port": internal_doctor_port},
    ]

    host = "127.0.0.1"
    threads_per_service = int(os.getenv("WSGI_THREADS", "6"))
    active_procs = []

    # 3. Launch each backend service in an isolated subprocess
    print("Starting backend WSGI workers with process-level isolation:")
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
            print(f"  [+] {name:<26} running on http://127.0.0.1:{port} ({threads_per_service} WSGI threads)")
            sys.stdout.flush()

            # Start background log streamer thread
            log_t = threading.Thread(target=stream_process_logs, args=(proc, name), daemon=True)
            log_t.start()
        except Exception as e:
            print(f"  [X] Failed to launch {name}: {e}")

    # 4. Initialize and launch Unified Gateway on public port
    routes = {
        "/shopkeeper": internal_shopkeeper_port,
        "/admin": internal_admin_port,
        "/delivery": internal_delivery_port,
        "/doctor": internal_doctor_port,
    }
    gateway = UnifiedGateway(routes=routes, customer_port=internal_customer_port)

    print("-" * 72)
    print(f"Unified Public Gateway listening on http://0.0.0.0:{gateway_port}")
    print("All 5 portals are accessible from your primary deployment URL:")
    print(f"  * Customer Storefront   -> http://localhost:{gateway_port}/")
    print(f"  * Live Project Hub      -> http://localhost:{gateway_port}/hub")
    print(f"  * Shopkeeper Portal     -> http://localhost:{gateway_port}/shopkeeper/")
    print(f"  * Super Admin Panel     -> http://localhost:{gateway_port}/admin/")
    print(f"  * Delivery Portal       -> http://localhost:{gateway_port}/delivery/")
    print(f"  * Doctor Telehealth     -> http://localhost:{gateway_port}/doctor/")
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

    # Launch Waitress for the Unified Gateway
    from waitress import serve
    try:
        serve(gateway, host="0.0.0.0", port=gateway_port, threads=8, _quiet=True)
    except KeyboardInterrupt:
        handle_exit(None, None)


if __name__ == "__main__":
    main()
