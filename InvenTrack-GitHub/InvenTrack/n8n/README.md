# n8n Workflow Setup

## Import the Workflow

1. Open your n8n instance (cloud or self-hosted)
2. Go to **Workflows** → click **Import**
3. Upload `inventrack_workflow.json`
4. The workflow will appear with all nodes pre-configured

---

## Configure Credentials

You need to set up credentials for 3 services:

### 1. Gmail (Alert emails)
- Go to **Settings → Credentials → New → Gmail OAuth2**
- Follow the Google OAuth setup flow
- In the "Alert" node, update the `sendTo` field with your email

### 2. Telegram Bot (Instant alerts)
- Create a bot via **@BotFather** on Telegram
- Get your **Bot Token** and your **Chat ID** (use @userinfobot)
- In n8n: **Settings → Credentials → New → Telegram API**
- In the "Send a text message" node, update `chatId`

### 3. Google Sheets (Logging)
- Create a new Google Sheet with these column headers in row 1:
  `Timestamp | Scanner | Asset | RSSI | Threshold | Status | Zone`
- Copy the Sheet ID from the URL:
  `https://docs.google.com/spreadsheets/d/[SHEET_ID]/edit`
- In n8n: **Settings → Credentials → New → Google Sheets OAuth2**
- In the "InvenTrack_Log" node, paste your Sheet ID

---

## Webhook URL

After importing, your webhook URL will be:
```
https://your-n8n-instance.com/webhook/pico-test
```

Copy this URL into your `pico2w_scanner.py` configuration.

---

## Hosting n8n for Free

For a persistent webhook URL, host n8n on [Render.com](https://render.com):
1. Fork the [n8n Docker template](https://docs.n8n.io/hosting/installation/docker/)
2. Deploy on Render as a Web Service
3. Use the provided Render URL as your webhook base

---

## Testing

Use the included Postman collection or send a manual POST:

```bash
curl -X POST https://your-n8n-instance.com/webhook/pico-test \
  -H "Content-Type: application/json" \
  -d '{
    "system": "InvenTrack",
    "scanner_id": "Pico2W_Scanner_01",
    "asset_id": "Tool_07",
    "ble_mac": "A4:C1:38:7B:91:22",
    "rssi": -90,
    "threshold_rssi": -75,
    "status": "OUT_OF_RANGE",
    "zone": "Ware House",
    "timestamp": "2026-02-28 10:15"
  }'
```

Expected response: `{ "message": "Workflow was started" }`
