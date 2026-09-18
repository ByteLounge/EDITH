# EDITH WebSocket Protocol Specification

This document details the real-time bidirectional message protocol between **EDITH Core**, **Client Controllers (Android)**, and **Device Agents (Windows / Future IoT)**.

---

## 1. Connection Endpoints

- **Device Endpoint**: `/ws/device?token=<DEVICE_TOKEN>`
  Used by device agents (e.g. Windows Agent, IoT microcontrollers).
- **Client Endpoint**: `/ws/client?token=<USER_JWT>`
  Used by user interfaces (e.g. Android app, Web dashboard).

All connections must be established over secure WebSockets (`wss://` in production, `ws://` in local development).

---

## 2. Base Message Envelope

All frames exchanged are UTF-8 encoded JSON objects conforming to:

```json
{
  "type": "string",
  "request_id": "string (UUIDv4)",
  "timestamp": "string (ISO 8601)",
  "payload": {}
}
```

---

## 3. Protocol Flow Diagrams

### 3.1 Device Registration & Heartbeat
```
Device Agent                          EDITH Core
     │                                     │
     │── [register] ──────────────────────>│ (Registers device & capabilities)
     │<── [register_ack] ──────────────────│ (Acknowledge connection)
     │                                     │
     │── [heartbeat] ─────────────────────>│ (Interval: 30s)
     │<── [heartbeat_ack] ─────────────────│
```

### 3.2 Command Execution Flow (Low / Medium Risk)
```
Android Client          EDITH Core           Windows Agent
     │                      │                      │
     │── [voice/text] ─────>│                      │
     │                      │── (Resolve intent)   │
     │                      │── [command] ────────>│
     │                      │                      │── (Execute capability)
     │                      │<── [command_result] ─│
     │<── [response] ───────│                      │
```

### 3.3 High-Risk Command Confirmation Flow
```
Android Client          EDITH Core           Windows Agent
     │                      │                      │
     │── "Shut down laptop" │                      │
     │                      │── (Risk = HIGH)      │
     │<── [confirm_req] ────│ (Needs confirmation) │
     │                      │                      │
     │── [confirm_res: YES] │                      │
     │                      │── [command] ────────>│
     │                      │<── [command_result] ─│
     │<── [response] ───────│                      │
```

---

## 4. Message Types & Schemas

### 4.1 Device Handshake: `register`
Sent by the device agent immediately upon establishing the WebSocket connection.

```json
{
  "type": "register",
  "request_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "timestamp": "2026-09-18T10:35:00Z",
  "payload": {
    "device_id": "laptop-main",
    "name": "Yash Laptop",
    "type": "computer",
    "platform": "windows",
    "version": "1.0.0",
    "capabilities": [
      "system_info",
      "battery_status",
      "open_application",
      "close_application",
      "volume_control",
      "media_control",
      "screenshot",
      "lock",
      "restart",
      "shutdown"
    ]
  }
}
```

Response from Core (`register_ack`):
```json
{
  "type": "register_ack",
  "request_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "timestamp": "2026-09-18T10:35:01Z",
  "payload": {
    "status": "authenticated",
    "device_id": "laptop-main",
    "heartbeat_interval_seconds": 30
  }
}
```

---

### 4.2 Heartbeat: `heartbeat`
```json
{
  "type": "heartbeat",
  "request_id": "c71e86a0-5b43-4e4b-9c6a-4cbfdb6f7a77",
  "timestamp": "2026-09-18T10:35:30Z",
  "payload": {
    "device_id": "laptop-main",
    "battery_level": 78,
    "is_charging": true
  }
}
```

Response from Core (`heartbeat_ack`):
```json
{
  "type": "heartbeat_ack",
  "request_id": "c71e86a0-5b43-4e4b-9c6a-4cbfdb6f7a77",
  "timestamp": "2026-09-18T10:35:30Z",
  "payload": {
    "status": "ok"
  }
}
```

---

### 4.3 Command: `command`
Dispatched by Core to the target device agent.

```json
{
  "type": "command",
  "request_id": "0fe4e719-74d3-455b-b9f0-d9d30fb0d312",
  "timestamp": "2026-09-18T10:36:00Z",
  "payload": {
    "device_id": "laptop-main",
    "capability": "open_application",
    "parameters": {
      "application": "vscode"
    }
  }
}
```

---

### 4.4 Command Result: `command_result`
Returned by device agent to Core.

```json
{
  "type": "command_result",
  "request_id": "0fe4e719-74d3-455b-b9f0-d9d30fb0d312",
  "timestamp": "2026-09-18T10:36:02Z",
  "payload": {
    "device_id": "laptop-main",
    "capability": "open_application",
    "success": true,
    "data": {
      "message": "Application 'vscode' launched successfully",
      "pid": 14220
    }
  }
}
```

Or on failure:
```json
{
  "type": "command_result",
  "request_id": "0fe4e719-74d3-455b-b9f0-d9d30fb0d312",
  "timestamp": "2026-09-18T10:36:02Z",
  "payload": {
    "device_id": "laptop-main",
    "capability": "open_application",
    "success": false,
    "error": {
      "code": "APPLICATION_NOT_ALLOWED",
      "message": "The application 'untrusted_app' is not in the system allowlist."
    }
  }
}
```

---

## 5. Standard Error Codes

| Error Code | HTTP Status | Description |
|---|---|---|
| `AUTHENTICATION_REQUIRED` | 401 | Missing or invalid authentication token |
| `PERMISSION_DENIED` | 403 | User does not have permission for the requested action |
| `DEVICE_NOT_FOUND` | 404 | Target device does not exist in the registry |
| `DEVICE_OFFLINE` | 503 | Target device is disconnected or unresponsive |
| `CAPABILITY_NOT_SUPPORTED` | 400 | Device does not advertise the requested capability |
| `APPLICATION_NOT_ALLOWED` | 403 | Target executable is not in the agent's safe allowlist |
| `INVALID_COMMAND` | 400 | Malformed command or parameters failed schema validation |
| `CONFIRMATION_REQUIRED` | 428 | High-risk command requires explicit user confirmation |
| `COMMAND_TIMEOUT` | 504 | Target device failed to respond within allotted timeout |
| `AI_PROVIDER_UNAVAILABLE` | 503 | Natural language provider (e.g. Ollama) unreachable |
| `DEVICE_EXECUTION_FAILED` | 500 | OS-level error during execution on target agent |
