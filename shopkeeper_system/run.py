"""
AcuMeds Shopkeeper App - Main Entry Point
Run this file to start the shopkeeper portal on port 5001
"""
import os
import sys
from app import create_app

# Create Flask app instance
app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    host = os.getenv('HOST', '0.0.0.0')
    debug = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    
    # Run on port 5001 (pharmacy app runs on 5000)
    app.run(debug=debug, host=host, port=port)