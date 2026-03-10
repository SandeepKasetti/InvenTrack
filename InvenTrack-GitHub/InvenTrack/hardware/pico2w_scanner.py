"""
InvenTrack - Raspberry Pi Pico 2W BLE Scanner
------------------------------------------------
Scans for ESP32 BLE beacon tags, reads RSSI,
and sends a JSON payload to the n8n webhook.

Hardware: Raspberry Pi Pico 2W
Firmware: MicroPython (with bluetooth + urequests)
"""

import bluetooth
import network
import urequests
import ujson
import time
import struct

# ─── CONFIGURATION ──────────────────────────────────────────────────────────
WIFI_SSID       = "YOUR_WIFI_SSID"
WIFI_PASSWORD   = "YOUR_WIFI_PASSWORD"

N8N_WEBHOOK_URL = "https://your-n8n-instance.onrender.com/webhook-test/pico-test"

SCANNER_ID      = "Pico2W_Scanner_01"
ZONE            = "Ware House"
THRESHOLD_RSSI  = -75          # dBm — below this = OUT_OF_RANGE

# Map BLE advertisement names → asset IDs
ASSET_MAP = {
    "IT_Tool01": "Tool_01",
    "IT_Tool02": "Tool_02",
    "IT_Tool07": "Tool_07",
    # Add more as needed
}

SCAN_DURATION_MS = 5000        # Scan for 5 seconds per cycle
SCAN_INTERVAL_MS = 10000       # Wait 10 seconds between cycles
# ─────────────────────────────────────────────────────────────────────────────

# ── Wi-Fi Connection ──────────────────────────────────────────────────────────
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    print("[InvenTrack] Connecting to Wi-Fi", end="")
    timeout = 20
    while not wlan.isconnected() and timeout > 0:
        print(".", end="")
        time.sleep(1)
        timeout -= 1
    if wlan.isconnected():
        print(f"\n[InvenTrack] Connected! IP: {wlan.ifconfig()[0]}")
    else:
        print("\n[InvenTrack] Wi-Fi connection FAILED")
    return wlan.isconnected()


# ── BLE Scanning ──────────────────────────────────────────────────────────────
discovered = {}   # { ble_mac: { name, rssi } }

def bt_irq(event, data):
    """BLE IRQ callback — called for each advertisement received."""
    if event == bluetooth.IRQ_SCAN_RESULT:
        addr_type, addr, adv_type, rssi, adv_data = data
        mac = ":".join("{:02X}".format(b) for b in bytes(addr))
        name = decode_name(bytes(adv_data))
        if name and name in ASSET_MAP:
            discovered[mac] = {"name": name, "rssi": rssi}

def decode_name(adv_data: bytes) -> str | None:
    """Extract Complete/Shortened Local Name from raw advertisement data."""
    i = 0
    while i < len(adv_data):
        length = adv_data[i]
        if length == 0:
            break
        ad_type = adv_data[i + 1]
        if ad_type in (0x08, 0x09):   # Shortened / Complete Local Name
            return adv_data[i + 2: i + 1 + length].decode("utf-8", "ignore")
        i += 1 + length
    return None


# ── HTTP Reporting ────────────────────────────────────────────────────────────
def send_event(mac: str, asset_id: str, rssi: int):
    status = "OUT_OF_RANGE" if rssi < THRESHOLD_RSSI else "IN_RANGE"
    payload = {
        "system":         "InvenTrack",
        "scanner_id":     SCANNER_ID,
        "asset_id":       asset_id,
        "ble_mac":        mac,
        "rssi":           rssi,
        "threshold_rssi": THRESHOLD_RSSI,
        "status":         status,
        "zone":           ZONE,
        "timestamp":      get_timestamp(),
    }
    print(f"[InvenTrack] Sending → {asset_id} | RSSI: {rssi} | {status}")
    try:
        resp = urequests.post(
            N8N_WEBHOOK_URL,
            headers={"Content-Type": "application/json"},
            data=ujson.dumps(payload),
        )
        print(f"[InvenTrack] Response: {resp.status_code}")
        resp.close()
    except Exception as e:
        print(f"[InvenTrack] HTTP error: {e}")

def get_timestamp() -> str:
    t = time.localtime()
    return "{:04d}-{:02d}-{:02d} {:02d}:{:02d}".format(
        t[0], t[1], t[2], t[3], t[4]
    )


# ── Main Loop ─────────────────────────────────────────────────────────────────
def main():
    if not connect_wifi():
        return

    ble = bluetooth.BLE()
    ble.active(True)
    ble.irq(bt_irq)

    while True:
        discovered.clear()
        print("[InvenTrack] Scanning for BLE beacons...")
        ble.gap_scan(SCAN_DURATION_MS, 30000, 30000)
        time.sleep_ms(SCAN_DURATION_MS + 500)
        ble.gap_scan(None)   # Stop scan

        if discovered:
            for mac, info in discovered.items():
                asset_id = ASSET_MAP.get(info["name"])
                if asset_id:
                    send_event(mac, asset_id, info["rssi"])
        else:
            print("[InvenTrack] No known beacons detected in this cycle.")

        time.sleep_ms(SCAN_INTERVAL_MS)


main()
