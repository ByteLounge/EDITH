# EDITH: Extensible Device Interface & Telemetric Host

> **Personal AI Assistant for Seamless, Secure Cross-Device Natural Language Control**

EDITH is a production-grade personal AI device coordination system designed to control your computers, phones, and future smart home hardware through voice and text. Rather than coupling LLMs directly to operating system shells, EDITH implements a **capability-constrained, zero-trust architecture** where natural language commands are translated into strictly-validated tool invocations executed by sandboxed device agents.

---

## 1. What EDITH Is

EDITH enables you to interact with your physical devices through intuitive natural language spoken from your Android phone:
- *"EDITH, open VS Code on my laptop."*
- *"EDITH, what's my laptop battery?"*
- *"EDITH, mute my laptop."*
- *"EDITH, take a screenshot of my laptop."*
- *"EDITH, lock my laptop."*
- *"EDITH, shut down my laptop."* *(Requires explicit confirmation)*

### Primary Supported Ecosystem
1. **Android Smartphone**: The primary voice & touch command center (Jetpack Compose, Speech-to-Text, Text-to-Speech).
2. **Windows Computer**: Controlled endpoint agent running in the system tray with an allowlisted application launcher and Win32 hardware control.
3. **EDITH Core**: Central async coordinator managing authentication, device registry, AI intent parsing, permission checks, and WebSocket routing.
4. **Future Hardware**: Designed for zero-rewrite addition of ESP32, smart plugs, lights, and IoT sensors.

---

## 2. Architecture & Security Guarantee

```
User (Voice / Text)
       │
       ▼
Android Client (SpeechRecognizer / Compose UI)
       │ (TLS / WSS)
       ▼
EDITH Core Orchestrator (FastAPI)
       │
       ▼
AI Provider (Ollama / Gemini / OpenAI)
       │ (Strict Function / Tool Calling Only)
       ▼
Structured Tool Call { action, device_id, parameters }
       │
       ▼
Permission & Risk Level Engine (LOW / MEDIUM / HIGH)
       │ (HIGH risk requires interactive user confirmation)
       ▼
Device Capability Validator (Registry)
       │
       ▼
Target Device Agent (Windows Agent via WebSocket)
       │ (Enforces local application allowlist; NO arbitrary shell execution)
       ▼
Local OS API Execution (Win32, psutil, ctypes)
       │
       ▼
Structured Result (Success / Error Code)
       │
       ▼
Response Synthesis (EDITH Core)
       │
       ▼
Android Client (UI Card + Voice TTS Announcement)
```

> **NEVER ARBITRARY SHELL**: The LLM NEVER receives bash, cmd, or PowerShell shell access. Device agents enforce strict application allowlists (`allowed_apps.json`) and specific Win32 API calls.

---

## 3. Repository Structure

```
edith/
├── README.md                 # System overview and quickstart
├── .env.example              # Environment variables template
├── docker-compose.yml        # PostgreSQL & backend container configuration
│
├── backend/                  # EDITH Core FastAPI Coordinator
│   ├── app/
│   │   ├── main.py           # FastAPI application entrypoint
│   │   ├── config/           # Pydantic settings & environment
│   │   ├── api/              # REST routes (auth, devices, commands)
│   │   ├── auth/             # JWT authentication & password hashing
│   │   ├── devices/          # Device registry and state management
│   │   ├── commands/         # Command processing and dispatching
│   │   ├── capabilities/     # Registered capability schemas & validators
│   │   ├── ai/               # AI provider abstraction (Ollama, OpenAI, Gemini)
│   │   ├── permissions/      # Risk level evaluation & confirmation manager
│   │   ├── database/         # SQLAlchemy models & repository layer
│   │   └── websocket/        # Real-time WebSocket connection manager
│   ├── tests/                # Comprehensive unit and integration test suite
│   └── requirements.txt
│
├── windows-agent/            # Windows Desktop Agent
│   ├── edith_agent/
│   │   ├── main.py           # Agent launcher & tray icon
│   │   ├── connection/       # WebSocket client with auto-reconnection
│   │   ├── commands/         # Command dispatcher
│   │   ├── capabilities/     # System capability discovery
│   │   ├── system/           # Win32, psutil, and volume integrations
│   │   ├── security/         # Application allowlist & credential storage
│   │   └── config/           # Local agent configuration
│   ├── tests/                # Agent unit tests
│   └── requirements.txt
│
├── android/EDITH/            # Android Mobile Application (Jetpack Compose)
│   └── app/                  # UI, ViewModels, Speech, Network, Keystore
│
└── docs/                     # Detailed architectural specifications
    ├── architecture.md
    ├── api.md
    ├── protocol.md
    ├── security.md
    ├── setup.md
    └── roadmap.md
```

---

## 4. How to Run Backend

1. **Navigate to backend**:
   ```bash
   cd backend
   ```
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure environment**:
   ```bash
   cp ../.env.example .env
   ```
4. **Start the server**:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
   API Documentation available at: `http://localhost:8000/docs`

---

## 5. How to Run Windows Agent

1. **Navigate to windows-agent**:
   ```bash
   cd windows-agent
   ```
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Pair the Agent**:
   ```bash
   python -m edith_agent.main --pair
   # Enter the 6-digit pairing code shown in Android App / generated from backend
   ```
4. **Run the Agent**:
   ```bash
   python -m edith_agent.main
   ```
   The agent will run in the Windows System Tray with persistent auto-reconnecting WebSocket connectivity.

---

## 6. How to Run Android Application

1. Open `android/EDITH` in **Android Studio**.
2. Update backend server host in `app/src/main/res/values/config.xml` (e.g. `http://10.0.2.2:8000` for emulator or `http://<LAN-IP>:8000` for physical phone).
3. Build and launch on your Android device (`Run 'app'`).
4. Log in or create an account, then tap **Add Device** to generate a pairing code.

---

## 7. How to Configure Ollama

EDITH uses Ollama for private, local LLM-powered tool calling.

1. Install and start Ollama:
   ```bash
   ollama serve
   ```
2. Pull the recommended tool-calling model:
   ```bash
   ollama pull llama3.2
   ```
3. In your `.env`:
   ```ini
   AI_PROVIDER=ollama
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=llama3.2
   ```
   *Note: If Ollama is offline, EDITH gracefully returns clear status messages and retains full direct button control.*

---

## 8. Device Pairing Flow

1. In the Android app, navigate to **Settings > Devices > Pair New Device**.
2. The backend generates a secure, 6-digit one-time pairing code with a 5-minute expiration window.
3. On your Windows laptop, run `python -m edith_agent.main --pair` and input the 6-digit code.
4. Backend verifies the code, creates a unique cryptographic device token, and links the laptop to your user account.
5. Windows Agent saves its device token in the Windows Credential Store and establishes its authenticated WebSocket session.

---

## 9. Example Voice & Text Commands

| Command | Action | Risk Tier |
|---|---|---|
| *"EDITH, what's my laptop battery?"* | Queries `psutil` battery level & charging state | LOW |
| *"EDITH, open VS Code on my laptop."* | Launches `Code.exe` from allowlist | LOW |
| *"EDITH, increase volume."* | Steps Windows master volume up via Win32 endpoint | LOW |
| *"EDITH, take a screenshot of my laptop."* | Captures desktop screen buffer | MEDIUM |
| *"EDITH, lock my laptop."* | Invokes Win32 `LockWorkStation` API | HIGH (Confirmed) |
| *"EDITH, restart my laptop."* | Schedules safe OS restart | HIGH (Confirmed) |
| *"EDITH, shut down my laptop."* | Initiates system shutdown sequence | HIGH (Confirmed) |

---

## 10. Security Model Summary

- **Zero Arbitrary Execution**: Device agents reject raw commands; only defined capabilities with allowlisted parameters are recognized.
- **Strict Risk Tiers**: Destructive actions (lock, reboot, shutdown) require explicit user confirmation via prompt dialog or voice "yes".
- **Token Security**: Device keys and user JWT tokens are stored securely in Windows Credential Store and Android Keystore.
- **Privacy First**: Voice audio is never stored; only transcribed commands appear in the auditable history.
