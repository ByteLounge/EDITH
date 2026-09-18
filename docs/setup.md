# EDITH Setup & Installation Guide

This guide details how to set up, configure, and execute the EDITH system across the backend, Windows Agent, and Android client.

---

## 1. Prerequisites

- **Python 3.12+**
- **Git**
- **Docker & Docker Compose** (optional for PostgreSQL; SQLite is supported for rapid local development)
- **Ollama** installed locally (or access to an OpenAI/Gemini-compatible API)
- **Android Studio** (for building/installing Android APK on phone or emulator)

---

## 2. Quickstart: Backend Server

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\Activate.ps1
   # On Linux/macOS:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment:
   Copy `.env.example` to `.env` and configure:
   ```ini
   SECRET_KEY=your-super-secret-jwt-key
   DATABASE_URL=sqlite+aiosqlite:///./edith.db
   AI_PROVIDER=ollama
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=llama3.2
   ```
5. Start the backend:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
6. Access Swagger API docs at `http://localhost:8000/docs`.

---

## 3. Quickstart: Windows Agent

1. Navigate to the Windows Agent directory:
   ```bash
   cd windows-agent
   ```
2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Pair or configure credentials:
   Run the pairing utility or enter the pairing code generated from the Android app / backend:
   ```bash
   python -m edith_agent.main --pair
   ```
5. Run the background agent:
   ```bash
   python -m edith_agent.main
   ```
   The agent will appear in the Windows System Tray and establish a persistent WebSocket connection with EDITH Core.

---

## 4. Quickstart: Android Client

1. Open `android/EDITH` in **Android Studio**.
2. Sync Gradle dependencies.
3. Configure `BACKEND_URL` in `app/src/main/res/values/config.xml` or build config to point to your backend server host (e.g. `http://10.0.2.2:8000` for emulator or `http://<your-lan-ip>:8000` for physical phone).
4. Build and run the app on your Android device:
   ```bash
   ./gradlew assembleDebug
   ```
5. Grant Microphone permission when prompted.

---

## 5. Ollama AI Setup

1. Start Ollama:
   ```bash
   ollama serve
   ```
2. Pull the recommended lightweight model:
   ```bash
   ollama pull llama3.2
   ```
3. Verify Ollama API:
   ```bash
   curl http://localhost:11434/api/tags
   ```
