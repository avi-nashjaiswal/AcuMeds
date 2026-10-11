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

## 🛡️ License

This project is licensed under the [MIT License](LICENSE).
