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
    # Ensure the shared database exists (same DB used by all 4 systems)
    db_path = os.path.join(os.path.dirname(__file__), '..', 'admin_system', 'database', 'pharmacy.db')
    db_path = os.path.abspath(db_path)
    if not os.path.exists(db_path):
        print("Database not found. Initializing...")
        from database.db_init import init_db
        init_db()
    
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5000)
