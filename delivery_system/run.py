"""
AcuMeds Delivery App - Main Entry Point
Run this file to start the delivery portal on port 5003
"""
from app import create_app

import os

app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5003))
    host = os.getenv('HOST', '0.0.0.0')
    debug = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    
    print(f"[+] Delivery Portal starting on http://{host}:{port}")
    if not debug:
        try:
            from waitress import serve
            serve(app, host=host, port=port, threads=int(os.getenv('WSGI_THREADS', '6')), _quiet=True)
        except ImportError:
            app.run(debug=debug, host=host, port=port)
    else:
        app.run(debug=debug, host=host, port=port)


