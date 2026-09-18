# EDITH Security & Trust Architecture

Security and safety are fundamental tenets of the EDITH design. Under no circumstances does EDITH permit untrusted, arbitrary code execution or unconstrained shell interaction.

---

## 1. Core Threat Model & Mitigations

### 1.1 Threat: Prompt Injection / Malicious LLM Tool Invocation
- **Risk**: An attacker manipulates natural language input (or indirect injection through webpage text or documents) to invoke destructive commands (e.g., `rm -rf`, format disk, download malware).
- **Mitigation**:
  1. **Strict Capability Whitelist**: The LLM output is parsed against a closed, strongly-typed tool schema. Unrecognized actions are rejected at the backend parser level.
  2. **Device-Side Whitelist Enforcement**: The target device agent (Windows Agent) does not execute arbitrary shell commands (`subprocess.run(shell=True)` is forbidden). It only executes allowlisted applications and discrete Win32 system APIs (`LockWorkStation`, `ExitWindowsEx`).
  3. **High-Risk Confirmation Barrier**: Destructive actions (`shutdown`, `restart`, session termination) trigger an out-of-band confirmation request requiring physical or explicit UI acknowledgement before execution.

### 1.2 Threat: Man-in-the-Middle (MITM) & Unauthorized Device Impersonation
- **Risk**: Interception or spoofing of commands across the public internet.
- **Mitigation**:
  1. **TLS / WSS Enforcement**: All communication utilizes TLS 1.3 / WSS.
  2. **Cryptographic Device Credentials**: Each device agent authenticates using a unique, cryptographically generated device secret issued during device pairing.
  3. **Short-Lived JWT Access Tokens**: User clients authenticate via short-lived JWT access tokens with secure refresh token rotation.

### 1.3 Threat: Device Hijacking via Credential Leakage
- **Risk**: Hardcoded secrets or tokens stored in plaintext files on disk.
- **Mitigation**:
  1. **Platform Credential Stores**:
     - **Windows**: Windows Credential Manager or DPAPI-protected storage.
     - **Android**: Android Keystore with encrypted SharedPreferences.
  2. **Pairing Codes**: Short-lived (5-minute expiration) numeric/alphanumeric pairing codes generated on demand.

---

## 2. Risk Level Matrix

Every capability in EDITH is assigned a strict risk classification:

| Risk Level | Operations | Confirmation Required | Execution Safeguards |
|---|---|---|---|
| **LOW** | `system_info`, `battery_status`, `volume_control`, `media_control`, `open_application` | No | Target app must match local `allowed_apps.json` allowlist |
| **MEDIUM** | `close_application`, `send_notification`, `ring_phone`, `take_screenshot` | Optional / Configurable | Memory-only buffers for screenshots, rate-limited |
| **HIGH** | `lock`, `restart`, `shutdown` | **Yes (Mandatory)** | Requires active confirmation token from the user interface |

---

## 3. Allowed Application Strategy (Windows Agent)

The Windows agent enforces an explicit application directory dictionary. An example configuration (`allowed_apps.json`):

```json
{
  "vscode": "Code.exe",
  "chrome": "chrome.exe",
  "spotify": "Spotify.exe",
  "notepad": "notepad.exe",
  "calculator": "calc.exe",
  "terminal": "wt.exe"
}
```

If the LLM emits `open_application(app="powershell -enc ...")` or an application not found in the configuration, the agent immediately rejects the command with `APPLICATION_NOT_ALLOWED`.

---

## 4. Audit Logging & Privacy

1. **No Audio Retention**: Raw voice audio from Android's `SpeechRecognizer` is processed locally or in memory and discarded. Only transcribed command strings are saved to the audit log if command history is enabled.
2. **Sanitized Logs**: Passwords, JWTs, device keys, and sensitive payload tokens are systematically filtered from all log streams.
3. **Data Sovereignty**: The user can purge command history, revoke paired devices, and disconnect agents instantly from the Settings screen.
