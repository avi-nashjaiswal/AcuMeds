"""
AcuMeds Delivery App - Main Entry Point
Run this file to start the delivery portal on port 5003
"""
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5003)
