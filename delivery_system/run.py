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
    app.run(debug=debug, host=host, port=port)

