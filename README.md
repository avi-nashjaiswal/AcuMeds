# 🏥 AcuMeds: AI-Powered Smart E-Pharmacy & Doctor Consultation System

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg?logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Framework-Flask-black.svg?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![AI / ML](https://img.shields.io/badge/AI%2FML-BioBERT%20%7C%20SHAP%20%7C%20LIME-orange.svg)](https://github.com/slundberg/shap)
[![WebRTC](https://img.shields.io/badge/Telehealth-In--App%20WebRTC-green.svg)](https://webrtc.org/)
[![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)](LICENSE)

> **AcuMeds** is an integrated five-portal decentralized healthcare framework synthesizing natural language symptom triaging, **Explainable Artificial Intelligence (XAI)** medicine recommendation, real-time peer-to-peer **WebRTC** clinical consultations, and fraud-resistant financial settlement.

---

## 🌟 Key Highlights & Capabilities

- 🤖 **Explainable AI (XAI) Medicine Recommendation**: Clinical symptom triaging using TF-IDF & BioBERT with token-level feature attribution maps powered by **SHAP** (Shapley Additive exPlanations) and **LIME** (Local Interpretable Model-agnostic Explanations).
- 📹 **Native In-App WebRTC Tele-Consultation**: Sub-120 ms latency peer-to-peer video streaming over STUN/ICE without third-party iframe crashes, integrated with real-time clinical chat and device fallbacks.
- 💊 **HMAC-SHA256 Signed Digital Prescriptions (Rx)**: Doctors issue tamper-evident digital prescriptions that instantly sync into the patient's cart for 1-click dispensing.
- 🛡️ **Replay-Proof 12-Digit UTR Payment Engine**: Atomic validation algorithm preventing payment replay attacks and enforcing non-repudiation across multi-vendor checkouts.
- 🏬 **End-to-End Pharmacy Supply Chain**: Multi-tier vendor licensing, cold-chain batch tracking, inventory thresholds, and delivery dispatch.

---

## 🏗️ The 5 Synchronized Portals

AcuMeds orchestrates five interconnected portals running concurrently over a unified relational core:

| Portal | Port | URL | Demo Credentials | Key Features |
| :--- | :---: | :--- | :--- | :--- |
| **Pharmacy / Customer** | `5000` | [http://localhost:5000](http://localhost:5000) | Public (Register or Login) | Medicine search, AI symptom triaging, cart checkout, video consult room |
| **Shopkeeper Portal** | `5001` | [http://localhost:5001](http://localhost:5001) | `shopkeeper1` / `shopkeeper123` | Inventory, prescription approval, batch management, POS order dispatch |
| **Admin Portal** | `5002` | [http://localhost:5002](http://localhost:5002) | `admin` / `admin123` | Vendor verification, KYC audit, UTR transactions, platform analytics |
| **Delivery Portal** | `5003` | [http://localhost:5003](http://localhost:5003) | `delivery1` / `delivery123` | Order pickup routing, delivery status updates, OTP confirmation |
| **Doctor Portal** | `5004` | [http://localhost:5004](http://localhost:5004) | `dr.smith` / `doctor123` | Patient appointment queue, WebRTC consultation room, Rx generation |

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.10 or higher
- Git

### 2. Clone the Repository
```bash
git clone https://github.com/avi-nashjaiswal/AcuMeds.git
cd AcuMeds
```

### 3. Set Up Virtual Environment & Dependencies
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Windows Command Prompt:
.venv\Scripts\activate.bat
# Linux/macOS:
source .venv/bin/activate

# Install requirements
pip install -r pharmacy_system/requirements.txt
```

### 4. Launch All 5 Portals Simultaneously

Run the unified multi-system runner:
```bash
# Using Python directly:
python run_all.py

# Or via Windows batch script:
start_all.bat

# Or via PowerShell script:
.\start_all.ps1
```

Once launched, visit the **AcuMeds Live Hub** at `http://localhost:5000` or open [AcuMeds_Live_Hub.html](AcuMeds_Live_Hub.html) in your browser to access all five portals from a single unified launcher.

---

## 📂 Project Architecture

```
AI MEDICAL/
├── pharmacy_system/       # Customer storefront, AI diagnosis & patient consultation
├── shopkeeper_system/     # Pharmacy vendor dashboard, inventory & dispatch
├── admin_system/          # Superadmin panel, vendor licensing & UTR fraud auditing
├── delivery_system/       # Delivery agent order tracking & OTP verification
├── doctor_system/         # Doctor portal, WebRTC tele-consultation & Rx generation
├── scripts/               # Publication generators & IEEE paper build tools
├── run_all.py             # Simultaneous multi-portal orchestrator & monitor
├── start_all.bat          # 1-Click launcher batch script
├── start_all.ps1          # PowerShell launcher script
├── AcuMeds_Live_Hub.html  # Central dashboard linking all 5 services
└── AcuMeds_AI_Medical_IEEE_Paper.pdf # Complete IEEE publication manuscript
```

---

## 🔬 Research & Publication

This system is accompanied by a full IEEE research manuscript:
- **Title**: *AcuMeds: An AI-Powered Smart E-Pharmacy and Doctor Consultation System with Explainable Medicine Recommendation*
- **Paper Formats**: [HTML](AcuMeds_AI_Medical_IEEE_Paper.html) | [Markdown](AcuMeds_AI_Medical_IEEE_Paper.md) | [PDF](AcuMeds_AI_Medical_IEEE_Paper.pdf) | [DOCX](AcuMeds_AI_Medical_IEEE_Paper.docx)

---

## 🌐 Production Deployment Guide

AcuMeds is engineered with a production-grade multi-service WSGI architecture. All five portals communicate over a shared transactional database with persistent upload storage.

### 🏆 Recommended Deployment Architectures

| Deployment Target | Suitable For | WSGI Runner | Database Strategy | Recommended Spec |
| :--- | :--- | :--- | :--- | :--- |
| **Linux VPS (Docker Compose)** *(Recommended)* | Full production, scalable, multi-domain | Nginx + Gunicorn / Waitress | SQLite on persistent volume OR Managed PostgreSQL | 2 vCPU, 2-4 GB RAM, Ubuntu 22.04+ (DigitalOcean, AWS Lightsail, Hetzner) |
| **Render.com** | 1-Click Cloud PaaS with SSL | Waitress / Gunicorn via Docker | 10 GB Persistent Disk (Blueprint included) | Starter plan or above |
| **Railway / Fly.io** | Fast containerized deployments | Dockerfile runner | Attached Volume | Standard container |
| **Bare Metal / Virtual Machine** | On-premise clinics / hospitals | Systemd + Nginx + Waitress | Local SQLite / PostgreSQL | Linux / Windows Server |

---

### Method 1: Production Deployment with Docker Compose (Recommended)

Docker Compose bundles all 5 WSGI services, database persistence, media volume storage, and an Nginx reverse proxy with health checks.

```bash
# 1. Clone repository on your production server
git clone https://github.com/avi-nashjaiswal/AcuMeds.git
cd AcuMeds

# 2. Configure production secrets
cp .env.production.example .env.production
# Edit .env.production and set your SECRET_KEY and payment/SMS credentials

# 3. Build and launch all containers in detached mode
docker compose up -d --build

# 4. Verify running services and health status
docker compose ps
docker compose logs -f
```

Once running:
- **Unified Gateway & Live Hub**: `http://your-server-ip/` or `http://your-server-ip/hub`
- **Customer Storefront**: `http://your-server-ip:5000`
- **Shopkeeper Portal**: `http://your-server-ip:5001`
- **Admin Panel**: `http://your-server-ip:5002`
- **Delivery Portal**: `http://your-server-ip:5003`
- **Doctor Telehealth**: `http://your-server-ip:5004`

---

### Method 2: Standalone Production Server (`prod_server.py`)

Run all five portals concurrently using the built-in multi-threaded Waitress WSGI orchestrator:

```bash
# 1. Install production dependencies
pip install -r requirements.txt

# 2. Run automated schema migration check
python migrate_db.py
python init_doctor_db.py

# 3. Launch the production WSGI server
# On Linux / macOS:
python prod_server.py

# On Windows:
start_production.bat
```

---

### Method 3: 1-Click Deployment to Render (`render.yaml`)

1. Fork or push this repository to your GitHub account (`https://github.com/avi-nashjaiswal/AcuMeds`).
2. In [Render Dashboard](https://dashboard.render.com/), create a new **Web Service** with:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python prod_server.py`
3. All 5 portals are automatically served under your single Render URL via the **Unified Cloud Gateway**:

| Portal / Feature | Live URL Path | Description & Credentials |
| :--- | :--- | :--- |
| **User / Customer** | `https://acumeds.onrender.com/` | Public storefront, AI recommendation, online cart |
| **Live Project Hub** | `https://acumeds.onrender.com/hub` | Interactive 1-click dashboard linking to all portals |
| **Shopkeeper Portal**| `https://acumeds.onrender.com/shopkeeper/` | Inventory, batch expiry, orders (`shopkeeper1` / `shopkeeper123`) |
| **Admin Panel** | `https://acumeds.onrender.com/admin/` | Superadmin console, UTR verify (`admin` / `admin123`) |
| **Doctor Telehealth**| `https://acumeds.onrender.com/doctor/` | Video consults & digital Rx (`doctor1` / `doctor123`) |
| **Delivery Portal** | `https://acumeds.onrender.com/delivery/` | Transit tracking & OTP proof (`delivery1` / `delivery123`) |

---

### Method 4: Production Linux VPS Service (`systemd`)

To run AcuMeds as an automatic system service on Ubuntu/Debian:

```bash
# 1. Copy service unit to systemd
sudo cp acumeds.service /etc/systemd/system/

# 2. Reload daemon, enable auto-start on boot, and start service
sudo systemctl daemon-reload
sudo systemctl enable acumeds
sudo systemctl start acumeds

# 3. Check service status
sudo systemctl status acumeds
```

---

### 🔐 Production Environment Variables Checklist

| Variable | Description | Recommended Production Value |
| :--- | :--- | :--- |
| `FLASK_ENV` | Runtime environment | `production` |
| `FLASK_DEBUG` | Werkzeug debugger (must be disabled) | `False` |
| `SECRET_KEY` | Cryptographic session signing key | 64-char random hex (`python -c "import secrets; print(secrets.token_hex(32))"`) |
| `DATABASE_URL` | Relational database connection string | `sqlite:////app/admin_system/database/pharmacy.db` or PostgreSQL URI |
| `HOST` | WSGI listening interface | `0.0.0.0` |
| `MANUAL_UPI_ID` | UPI ID for UTR settlement | `yourname@okhdfcbank` |
| `SMS_PROVIDER` | Delivery & Rx OTP dispatch | `twilio` (live) or `console` (log simulation) |
| `OPENAI_API_KEY` | Key for Shopkeeper clinical AI assistant | `sk-proj-...` (optional) |

---

## 🛡️ License

This project is licensed under the [MIT License](LICENSE).

