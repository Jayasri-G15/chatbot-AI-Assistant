# BIRIYANI AI CHATBOT & CRM DASHBOARD

A beginner-friendly full-stack Multi-Agent AI Assistant and CRM application built with **FastAPI**, **React 19**, **TypeScript**, and **SQLite**.

---

## 🛠️ Key Features & Stack
- **Frontend**: React 19 + TypeScript + Vite + Tailwind CSS
- **Backend**: FastAPI (Python 3.10+) + SQLAlchemy + SQLite
- **AI Engine**: Multi-Agent Supervisor (NVIDIA NIM LLM integration)
- **Security**: JWT Authentication, User Isolation, Grounded RAG, and Security Guardrails
- **CRM Dashboard**: Real-time user activity, subscriptions, analytics, and Admin AI Assistant

---

## 🚀 Beginner Quickstart Guide

### Prerequisites
- Python 3.10+
- Node.js 18+
- NVIDIA API Key (provided in `.env`)

---

### Step 1: Start Backend Server
```bash
# 1. Navigate to backend folder
cd biriyani/backend

# 2. Create and activate Python virtual environment
python3 -m venv .venv
source .venv/bin/activate    # On Windows: .venv\Scripts\activate

# 3. Install requirements
pip install -r requirements.txt

# 4. Run backend server
python3 -m uvicorn app.main:app --reload --port 8000
```
Backend API will be live at: **http://localhost:8000**

---

### Step 2: Start Frontend Application
In a **new terminal window**:
```bash
# 1. Navigate to frontend folder
cd biriyani/frontend

# 2. Install dependencies
npm install

# 3. Start development server
npm run dev
```
Open **http://localhost:5173** in your web browser.

---

### 🔑 Demo Accounts & Login

#### Admin Account (Full Access + CRM Dashboard)
- **Email**: `jayasrijs1501@gmail.com`
- **Password**: `password123`

#### Standard User Account
- Create any new user via **Signup** on the login modal!

---

## 🧪 Running Backend Unit Tests
To verify all backend API endpoints, user isolation, and AI security:
```bash
python3 -m pytest biriyani/backend/tests/ -v
```
*(All 73 unit and E2E integration tests pass cleanly)*
