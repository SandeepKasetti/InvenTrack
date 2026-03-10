# Hardware Setup Guide

## Components Required

### Per ESP32 BLE Tag
| Component | Qty | Notes |
|---|---|---|
| ESP32 Development Board | 1 | Any variant (DevKit, WROOM, etc.) |
| LiPo Battery 3.7V 500mAh | 1 | For portable operation |
| LiPo Charger Module (TP4056) | 1 | Optional for rechargeable setup |
| Double-sided tape / zip tie | 1 | For attaching to tool |

### Per Pico 2W Scanner
| Component | Qty | Notes |
|---|---|---|
| Raspberry Pi Pico 2W | 1 | Must be the **W** (Wi-Fi) variant |
| USB-C Power Supply 5V/2A | 1 | For fixed installation |
| Enclosure / case | 1 | Optional, for protection |

---

## ESP32 Tag Setup

1. Install [MicroPython on ESP32](https://micropython.org/download/ESP32_GENERIC/)
2. Copy `esp32_ble_beacon.py` to the ESP32 as `main.py`
3. Edit the configuration section:
   ```python
   ASSET_ID = "Tool_01"      # Unique label for this asset
   BLE_NAME = "IT_Tool01"    # Must match ASSET_MAP on scanner side
   ```
4. Power cycle — the beacon starts advertising automatically.

---

## Pico 2W Scanner Setup

1. Install [MicroPython on Pico 2W](https://micropython.org/download/RPI_PICO2_W/)
2. Install `urequests` library:
   - Download `urequests.py` and copy to the Pico filesystem
3. Copy `pico2w_scanner.py` to the Pico as `main.py`
4. Edit the configuration section:
   ```python
   WIFI_SSID       = "YourWiFiName"
   WIFI_PASSWORD   = "YourPassword"
   N8N_WEBHOOK_URL = "https://your-n8n.onrender.com/webhook-test/pico-test"
   SCANNER_ID      = "Pico2W_Scanner_01"
   ZONE            = "Ware House"
   THRESHOLD_RSSI  = -75
   ```
5. Add your ESP32 tags to the `ASSET_MAP`:
   ```python
   ASSET_MAP = {
       "IT_Tool01": "Tool_01",
       "IT_Tool02": "Tool_02",
       # ...
   }
   ```
6. Power on — it connects to Wi-Fi and starts scanning automatically.

---

## Placement Tips

- **Scanners**: Mount at ~1–1.5m height, ideally at room corners for best coverage.
- **Tags**: Attach to tools with double-sided tape or a custom 3D-printed bracket.
- **Threshold tuning**: Walk a tool to your desired boundary edge and note the RSSI value — set `THRESHOLD_RSSI` to that value.

---

## Tested Coverage

| Setup | Coverage |
|---|---|
| 1 Scanner | ~5m radius in open space |
| 3 Scanners (triangle) | ~10×10m area |
| Through walls | Signal drops ~15–20 dBm per wall |
