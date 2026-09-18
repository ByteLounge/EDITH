# EDITH Architecture Roadmap & Future Expansions

This roadmap details post-MVP capabilities designed into the EDITH core architecture.

---

## 1. IoT & Embedded Device Expansion (ESP32 / Microcontrollers)

### Universal Device Abstraction
Future low-power microcontrollers (e.g. ESP32, Raspberry Pi Pico W) will integrate via lightweight MQTT or direct WebSocket bridges without requiring changes to EDITH Core.

```
ESP32 (MQTT) ──> [MQTT Broker] ──> [EDITH MQTT Bridge] ──> [EDITH Core /ws/device]
```

Planned capabilities for ESP32:
- `get_temperature`
- `get_humidity`
- `set_relay`
- `set_light_state`
- `dim_light`

---

## 2. Trigger-Condition-Action Automation Engine

The architecture includes hooks for an asynchronous event-driven rule engine:

```
TRIGGER                    CONDITION                    ACTION
[Battery < 20%]    ───>    [User is Home]       ───>    [Send Phone Notification]
[At 23:00]         ───>    [Laptop is Online]   ───>    [Lock Laptop]
[Motion Detected]  ───>    [Mode is Away]       ───>    [Sound Alarm & Alert]
```

### Automation Data Model
```json
{
  "rule_id": "rule_battery_saver_01",
  "name": "Low Battery Alert",
  "trigger": {
    "device_id": "laptop-main",
    "event": "battery_level_changed",
    "operator": "<=",
    "value": 20
  },
  "condition": {
    "time_window": "08:00-22:00"
  },
  "action": {
    "target_device": "phone-main",
    "capability": "send_notification",
    "parameters": {
      "title": "Battery Low",
      "body": "Laptop battery has dropped below 20%."
    }
  }
}
```

---

## 3. Intelligent User Memory & Personalization

Post-MVP memory architecture will feature:
- Device Alias Learning (e.g., automatically associating "work station" with `laptop-work` based on user corrections).
- Routine Recognition (detecting recurring commands at specific times of day).
- Privacy-preserved local vector store (Chromadb/FAISS) purely for contextual preference retrieval without storing raw microphone audio.

---

## 4. On-Device Wake-Word Engine

Future Android releases will incorporate an offline, ultra-low-power wake word engine (e.g., openWakeWord / Porcupine) triggering:
```
"Hey EDITH" ──> Wake Engine ──> Activate Audio Session ──> Speech Recognizer ──> Command Pipeline
```
