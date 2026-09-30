# Installation & Setup Guide

This guide walks through setting up and running the **AI Career Intelligence & Growth Platform** on local development machines.

---

## 1. System Requirements

- **Operating System**: Windows 10/11, macOS, or Linux
- **Python**: Python 3.10, 3.11, 3.12, or 3.13
- **Hardware**: 8 GB RAM (No GPU required)

---

## 2. Installation Steps

### Step 1: Clone Repository & Create Virtual Environment
```bash
# Clone the repository
git clone https://github.com/your-username/ai-career-intelligence.git
cd ai-career-intelligence

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Environment Configuration
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Optionally add your Google Gemini API key in `.env`:
```ini
GEMINI_API_KEY=your_gemini_api_key_here
DEMO_MODE=true
```
*(Note: If `DEMO_MODE=true`, the application runs with high-fidelity mock data and does not consume API quota).*

---

## 3. Running the Application

### Option A: Single-Command Concurrent Launcher (Recommended)
Launch both FastAPI backend and Streamlit UI together:
```bash
python run.py
```
- Streamlit UI will open at: `http://localhost:8501`
- FastAPI OpenAPI docs available at: `http://127.0.0.1:8000/docs`

### Option B: Run Backend and Frontend Separately

**Terminal 1 (FastAPI Backend)**:
```bash
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

**Terminal 2 (Streamlit Frontend)**:
```bash
streamlit run frontend/app.py
```

---

## 4. Running Automated Tests
```bash
python -m pytest tests/ -v --tb=short
```
