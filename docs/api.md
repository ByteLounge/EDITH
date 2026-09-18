# EDITH REST & WebSocket API Reference

The EDITH Core exposes REST endpoints for authentication, device pairing, and query dispatch, alongside WebSockets for real-time telemetry and command delivery.

---

## 1. Authentication Endpoints

### 1.1 Register User
- **Method**: `POST`
- **Path**: `/api/v1/auth/register`
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "SecurePassword123!",
    "full_name": "Yash"
  }
  ```
- **Response**: `201 Created`
  ```json
  {
    "user_id": "usr_9b1deb4d",
    "email": "user@example.com",
    "access_token": "eyJhbGciOi...",
    "refresh_token": "eyJhbGciOi...",
    "token_type": "bearer"
  }
  ```

### 1.2 Login User
- **Method**: `POST`
- **Path**: `/api/v1/auth/login`
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "SecurePassword123!"
  }
  ```
- **Response**: `200 OK`

### 1.3 Refresh Token
- **Method**: `POST`
- **Path**: `/api/v1/auth/refresh`
- **Request Body**:
  ```json
  {
    "refresh_token": "eyJhbGciOi..."
  }
  ```
- **Response**: `200 OK`

---

## 2. Device Management Endpoints

### 2.1 List User Devices
- **Method**: `GET`
- **Path**: `/api/v1/devices`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `200 OK`
  ```json
  [
    {
      "device_id": "laptop-main",
      "name": "Yash Laptop",
      "type": "computer",
      "platform": "windows",
      "status": "online",
      "capabilities": ["battery_status", "open_application", "screenshot", "lock"],
      "last_seen": "2026-09-18T10:30:00Z"
    }
  ]
  ```

### 2.2 Generate Pairing Code
- **Method**: `POST`
- **Path**: `/api/v1/devices/pair/code`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `201 Created`
  ```json
  {
    "pairing_code": "849201",
    "expires_at": "2026-09-18T10:35:00Z"
  }
  ```

### 2.3 Redeem Pairing Code (Device Agent)
- **Method**: `POST`
- **Path**: `/api/v1/devices/pair/claim`
- **Request Body**:
  ```json
  {
    "pairing_code": "849201",
    "device_name": "Yash Laptop",
    "device_type": "computer",
    "platform": "windows"
  }
  ```
- **Response**: `200 OK`
  ```json
  {
    "device_id": "laptop-main",
    "device_token": "dev_sec_78a1bc...",
    "ws_url": "wss://edith.example.com/ws/device"
  }
  ```

### 2.4 Update Device Name / Alias
- **Method**: `PATCH`
- **Path**: `/api/v1/devices/{device_id}`
- **Request Body**:
  ```json
  {
    "name": "Primary Workstation"
  }
  ```

### 2.5 Revoke Device
- **Method**: `DELETE`
- **Path**: `/api/v1/devices/{device_id}`
- **Response**: `204 No Content`

---

## 3. Command Execution & History

### 3.1 Send Natural Language Command
- **Method**: `POST`
- **Path**: `/api/v1/commands/process`
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "query": "EDITH, open VS Code on my laptop"
  }
  ```
- **Response**: `200 OK`
  ```json
  {
    "command_id": "cmd_0fe4e719",
    "status": "completed",
    "target_device_id": "laptop-main",
    "capability": "open_application",
    "speech_response": "VS Code is open on your laptop.",
    "text_response": "VS Code launched successfully on Yash Laptop.",
    "requires_confirmation": false
  }
  ```

### 3.2 Confirm High-Risk Command
- **Method**: `POST`
- **Path**: `/api/v1/commands/confirm`
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "confirmation_token": "conf_31298d02",
    "confirmed": true
  }
  ```

### 3.3 Fetch Command History
- **Method**: `GET`
- **Path**: `/api/v1/commands/history`
- **Headers**: `Authorization: Bearer <token>`
- **Query Params**: `limit=50&offset=0`
- **Response**: `200 OK`

---

## 4. Health & Diagnostics
- **Method**: `GET`
- **Path**: `/health`
- **Response**: `200 OK`
  ```json
  {
    "status": "healthy",
    "version": "1.0.0",
    "connected_devices": 2,
    "ai_provider": "ollama",
    "ai_status": "online"
  }
  ```
