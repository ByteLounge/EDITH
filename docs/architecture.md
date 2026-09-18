# EDITH Architecture Specification

## 1. System Overview

**EDITH** (Extensible Device Interface & Telemetric Host) is a personal AI assistant and device orchestration system designed to allow users to interact with and control their devices via natural language (voice and text) from an Android smartphone, desktop agents, and future IoT hardware.

### Core Architectural Principle

```
User (Android Voice / Text / Client)
       │
       ▼
Speech-to-Text (Android SpeechRecognizer / Whisper)
       │
       ▼
EDITH Core (FastAPI Backend Orchestrator)
       │
       ▼
AI Provider Layer (Ollama / Gemini / OpenAI)
       │  (Strict Function / Tool Calling Only)
       ▼
Structured Tool Call { action, device_id, parameters }
       │
       ▼
Permission & Risk Level Validator (LOW / MEDIUM / HIGH)
       │  (If HIGH: Requires Explicit User Confirmation)
       ▼
Device Registry & Capability Validator
       │  (Checks online status & advertised capabilities)
       ▼
WebSocket Communication Bus (/ws/device, /ws/client)
       │
       ▼
Target Device Agent (e.g. EDITH Windows Agent)
       │  (Local Allowlist & Safety Boundary Enforcement)
       ▼
Action Execution (Local OS APIs: psutil, pywin32, ctypes)
       │
       ▼
Execution Result { success: bool, data / error }
       │
       ▼
EDITH Core Event Coordinator
       │
       ▼
Response Generator (Natural Language Synthesis)
       │
       ▼
Client (Android UI + Android Text-to-Speech)
```

> **CRITICAL SECURITY GUARANTEE**: The LLM is **NEVER** given direct access to an operating system shell, arbitrary command execution, or raw code interpreters. The LLM acts exclusively as a natural language intent parser that generates strictly-typed, schema-validated tool invocations against registered device capabilities.

---

## 2. Core Components

### 2.1 EDITH Core (Backend Coordinator)
- **Framework**: Python 3.12+, FastAPI, Pydantic v2, SQLAlchemy (Async/Sync repository pattern for SQLite / PostgreSQL).
- **Authentication**: JWT-based authentication (access token, refresh token) and device-specific cryptographic / API tokens.
- **Device Registry**: In-memory and persistent tracking of connected devices, their operational platform, connection status (`ONLINE`, `OFFLINE`, `CONNECTING`), and advertised capabilities.
- **Natural Language Device Resolution**: Maps conversational references (e.g., *"my laptop"*, *"the computer"*, *"my phone"*) to canonical device IDs. Prompts user if multiple devices match.
- **Tool Calling & Risk Governance**: Evaluates tool calls against risk tiers:
  - `LOW`: Read-only queries (battery, system info), volume, media playback, allowlisted app launch.
  - `MEDIUM`: Notifications, window closing, non-destructive app termination.
  - `HIGH`: System lock, reboot, shutdown, OS settings modification. Requires interactive user confirmation.
- **WebSocket Protocol Engine**: Full-duplex persistent connections for device agents (`/ws/device`) and client controllers (`/ws/client`) with heartbeat ping/pong and correlation via `request_id`.

### 2.2 EDITH Windows Agent
- **Runtime**: Python 3.12+ lightweight desktop agent running in the Windows System Tray (`pystray` / background daemon).
- **Communication**: Persistent WSS/WS client with automatic backoff and reconnection logic.
- **Capability Discovery & Advertisement**: Detects host OS details, battery presence via `psutil`, audio session interfaces, and advertises supported capabilities on handshake.
- **Security Boundary**:
  - Application allowlist configuration (`allowed_apps.json`): Maps human-friendly names (e.g., `vscode`, `chrome`, `spotify`) to verified executable targets.
  - No dynamic `subprocess.run(shell=True)` or arbitrary PowerShell/cmd execution.
  - Direct Win32 APIs via `ctypes` and `pywin32` for session locking (`LockWorkStation`), system power, and volume control.
- **Screen & Media Engine**: Captures screenshots securely to memory buffers for transmission, controls media playback via virtual key events.

### 2.3 EDITH Android Application
- **UI Framework**: Modern Jetpack Compose with Material 3, Dark-first aesthetic with dynamic theming.
- **Voice Pipeline**: Android `SpeechRecognizer` for prompt capture, combined with Android `TextToSpeech` (TTS) for conversational vocal response.
- **Network Engine**: OkHttp WebSocket connection for real-time telemetry and command delivery, Retrofit/OkHttp REST for pairing and device management.
- **Local Security**: Android Keystore for secure token storage.
- **Screens**:
  1. *Home*: Status summary, online device badges, quick microphone activation, recent command preview.
  2. *Voice Assistant*: Interactive vocal console with speech waveform indicator, live transcript, and audio response controls.
  3. *Devices*: Device inventory cards displaying hardware type, real-time connectivity status, and supported capabilities.
  4. *Activity*: Auditable command history with execution timestamps, target device, and outcome status.
  5. *Settings*: Voice controls (speech rate, auto-speak), AI provider configuration, pairing controls, and privacy toggles.

---

## 3. Communication Protocol

All real-time communications flow through structured JSON messages over WebSocket channels.

### Message Envelope Specification
```json
{
  "type": "command | command_result | register | heartbeat | error | confirmation_request | confirmation_response",
  "request_id": "urn:uuid:6ba7b810-9dad-11d1-80b4-00c04fd430c8",
  "timestamp": "2026-09-18T10:30:00Z",
  "payload": {}
}
```

Every command is tracked via an idempotent `request_id`. The backend coordinates timeout handling (default: 10s) and notifies clients if a device drops connection during command processing.

---

## 4. Extensibility for Future IoT & Embedded Devices

The architecture defines a universal device interface:
1. **Handshake**: Device connects and emits a `register` packet containing its unique ID, hardware type, platform, and capability list.
2. **Heartbeat**: Periodic ping/pong packets ensure heartbeat liveness without polling.
3. **Capability Contract**: Future devices (e.g., ESP32 temperature sensor or relay switch) only need to advertise:
   ```json
   {
     "type": "register",
     "device_id": "esp32-living-room",
     "platform": "esp32",
     "capabilities": ["get_temperature", "set_relay", "get_humidity"]
   }
   ```
4. **Transport Independence**: An MQTT-to-WebSocket bridge can map low-power MQTT topics to EDITH Core device sockets without altering backend business logic.

---

## 5. Directory Structure

```
edith/
├── README.md
├── .gitignore
├── .env.example
├── docker-compose.yml
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config/
│   │   ├── api/
│   │   ├── auth/
│   │   ├── devices/
│   │   ├── commands/
│   │   ├── capabilities/
│   │   ├── ai/
│   │   ├── permissions/
│   │   ├── events/
│   │   ├── database/
│   │   ├── websocket/
│   │   ├── services/
│   │   └── utils/
│   ├── tests/
│   └── requirements.txt
│
├── android/
│   └── EDITH/
│       ├── app/
│       │   ├── src/main/java/com/edith/app/
│       │   └── build.gradle.kts
│       ├── gradle/
│       └── build.gradle.kts
│
├── windows-agent/
│   ├── edith_agent/
│   │   ├── main.py
│   │   ├── connection/
│   │   ├── commands/
│   │   ├── capabilities/
│   │   ├── system/
│   │   ├── security/
│   │   └── config/
│   ├── tests/
│   └── requirements.txt
│
├── docs/
│   ├── architecture.md
│   ├── api.md
│   ├── protocol.md
│   ├── security.md
│   ├── setup.md
│   └── roadmap.md
│
└── scripts/
    ├── dev/
    └── deployment/
```
