"""
InvenTrack - ESP32 BLE Beacon Tag
----------------------------------
Attach this to each tool/asset.
Broadcasts a BLE advertisement packet continuously.

Hardware: ESP32 (any variant)
Firmware: MicroPython
"""

import bluetooth
import time
import struct

# ─── CONFIGURATION ──────────────────────────────────────────────────────────
ASSET_ID    = "Tool_07"           # Unique name for this asset
BLE_NAME    = "IT_Tool07"         # BLE advertisement name (max ~15 chars)
ADV_INTERVAL_MS = 200             # Broadcast every 200ms
# ─────────────────────────────────────────────────────────────────────────────

ble = bluetooth.BLE()
ble.active(True)

def encode_adv_payload(name: str) -> bytes:
    """Build a minimal BLE advertisement payload with device name."""
    name_bytes = name.encode("utf-8")
    # Flags: LE General Discoverable, BR/EDR not supported
    flags = struct.pack("BBB", 2, 0x01, 0x06)
    # Complete Local Name
    name_ad = struct.pack("BB", len(name_bytes) + 1, 0x09) + name_bytes
    return flags + name_ad

def start_advertising():
    payload = encode_adv_payload(BLE_NAME)
    # interval in units of 0.625ms
    interval_units = int(ADV_INTERVAL_MS * 1000 / 625)
    ble.gap_advertise(interval_units, adv_data=payload)
    print(f"[InvenTrack] Beacon '{BLE_NAME}' advertising for asset '{ASSET_ID}'")

start_advertising()

# Keep the script alive
while True:
    time.sleep(10)
    print(f"[InvenTrack] {ASSET_ID} beacon alive...")
