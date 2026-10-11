"""
Main Flask application entry point
Run this file to start the server
"""
import os
import sys
from app import create_app

# Create Flask app instance
app = create_app()

# Register main blueprint - main_bp_final_unique already registered in create_app, skip duplicate
# from app.routes import main_bp
# app.register_blueprint(main_bp)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    debug = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    
    # Ensure shared database tables exist
    db_path = os.path.join(os.path.dirname(__file__), '..', 'admin_system', 'database', 'pharmacy.db')
    db_path = os.path.abspath(db_path)
    if not os.path.exists(db_path) and not os.getenv('DATABASE_URL'):
        print("Database not found. Initializing...")
        from database.db_init import init_db
        init_db()

    print(f"[+] Customer / Pharmacy Portal starting on http://{host}:{port}")
    if not debug:
        try:
            from waitress import serve
            serve(app, host=host, port=port, threads=int(os.getenv('WSGI_THREADS', '6')), _quiet=True)
        except ImportError:
            app.run(debug=debug, host=host, port=port)
    else:
        app.run(debug=debug, host=host, port=port)


