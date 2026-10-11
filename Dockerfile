# ==============================================================================
# AcuMeds - Production Multi-Portal Dockerfile
# Multi-portal AI E-Pharmacy, Doctor Telehealth, and Supply Chain Platform
# ==============================================================================
FROM python:3.11-slim-bullseye

# Set environment settings
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8 \
    FLASK_ENV=production \
    FLASK_DEBUG=False \
    PORT_PHARMACY=5000 \
    PORT_SHOPKEEPER=5001 \
    PORT_ADMIN=5002 \
    PORT_DELIVERY=5003 \
    PORT_DOCTOR=5004

# Install essential system dependencies (Pillow, PDF, Docx, networking, SQLite/PostgreSQL)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    libpq-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    procps \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python requirements
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy entire application codebase
COPY . /app/

# Create necessary runtime directories
RUN mkdir -p \
    /app/admin_system/database \
    /app/delivery_system/database \
    /app/shopkeeper_system/database \
    /app/static/uploads/medicines \
    /app/static/uploads/licenses \
    /app/static/uploads/prescriptions \
    /app/static/uploads/signatures \
    /app/logs

# Make scripts executable
RUN chmod +x /app/prod_server.py

# Expose all 5 portal ports and Render cloud port
EXPOSE 5000 5001 5002 5003 5004 10000

# Health check to ensure the primary service is responding
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD sh -c "curl -f http://localhost:\${PORT:-5000}/ || exit 1"

# Default command: launch the production WSGI multi-portal runner
CMD ["python", "prod_server.py"]

