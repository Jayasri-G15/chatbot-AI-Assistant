# BIRIYANI AI CHATBOT & CRM DASHBOARD

A full-stack Multi-Agent AI Assistant and CRM application built with **FastAPI**, **React 19**, **TypeScript**, and **SQLite**.

---

## 🛠️ Tech Stack & Features
- **Frontend**: React 19 + TypeScript + Vite + Tailwind CSS
- **Backend**: FastAPI (Python 3.10+) + SQLAlchemy + SQLite (`biriyani/backend/chat.db`)
- **AI Engine**: Multi-Agent Supervisor Architecture (NVIDIA NIM LLM integration)
- **Security**: JWT Authentication, User Isolation, Grounded RAG, and AI Security Guardrails
- **CRM Dashboard**: Real-time user activity, subscriptions, analytics, and Admin AI Assistant

---

## 🚀 How to Run the Project locally

### Prerequisites
- **Python**: Version 3.10 or higher installed
- **Node.js**: Version 18 or higher installed

---

### Step 1: Start Backend Server (`FastAPI`)

Open your terminal and run:

```bash
# 1. Navigate to the backend folder
cd biriyani/backend

# 2. Activate the Python virtual environment
source .venv/bin/activate    # On Windows: .venv\Scripts\activate

# 3. Ensure dependencies are installed
pip install -r requirements.txt

# 4. Start the FastAPI backend server
python3 -m uvicorn app.main:app --reload --port 8000
```

Backend server is live at: **`http://localhost:8000`** (Health check: `http://localhost:8000/health`)

---

### Step 2: Start Frontend Application (`React + Vite`)

Open a **new terminal window** and run:

```bash
# 1. Navigate to the frontend folder
cd biriyani/frontend

# 2. Install dependencies (if first time)
npm install

# 3. Start the Vite development server
npm run dev
```

Open **`http://localhost:5173`** in your web browser.

---

### 🔑 Login Credentials

#### 1. Admin Account (Full Access + Admin CRM Dashboard)
- **Email**: `jayasrijs1501@gmail.com`
- **Password**: `password123`

#### 2. Standard User Account
- Click **"Don't have an account? Sign up"** on the login screen to create a user account.

---

### 🔑 Environment Variables Setup (`.env`)

The backend configuration file is located at `biriyani/backend/.env`:

```env
NVIDIA_API_KEY=your_nvidia_api_key_here
LLM_API_KEY=your_nvidia_api_key_here
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
NVIDIA_MODEL=meta/llama-3.2-11b-vision-instruct
DATABASE_URL=sqlite:///./chat.db
CORS_ORIGINS=http://localhost:5173
JWT_SECRET_KEY=b79bf1f0ac47c5396d1731c9adec6c05c2d018e2b2b49f08ef2d455e651955b7
```

---

## 🧪 Running Automated Tests

To run the complete test suite (73 passing tests covering auth, RAG, guardrails, and CRM):

```bash
python3 -m pytest biriyani/backend/tests/ -v
```
