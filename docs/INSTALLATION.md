# Installation & Setup Guide

This guide walks you through setting up and launching the **AI-Powered Customer Support Agent** application locally.

---

## 1. System Requirements

- **Operating System**: Windows 10/11, macOS, or Linux.
- **Python**: Version 3.10 or newer (tested up to Python 3.14).
- **Web Browser**: Chrome, Edge, Firefox, or Safari.

---

## 2. Step-by-Step Installation

### Step 1: Navigate to Project Directory
```bash
cd ai-customer-support
```

### Step 2: Create a Python Virtual Environment

**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables (Optional)
```bash
cp .env.example .env
```
*(You can leave API keys blank initially to evaluate the system in zero-config offline mode with pre-seeded data).*

---

## 3. Launching the Application

Start the Flask server:
```bash
python run.py
```

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 4. 1-Click Evaluation Credentials

Use the pre-seeded evaluation credentials on `/login.html` (or click the 1-Click demo buttons):

| Role | Email | Password | Access Rights |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin@company.com` | `Admin@123` | Analytics, Knowledge Base (RAG), FAQs, All Tickets |
| **Support Agent** | `agent.rajesh@company.com` | `Agent@123` | Priority Ticket Queue, Customer Replies, Internal Notes |
| **Customer** | `customer@example.com` | `Customer@123` | Trilingual AI Chatbot, Ticket Tracker, Complaint Submission |

---

## 5. Running the Test Suite

Execute the 30 automated test cases with pytest:
```bash
python -m pytest tests/ -v
```
