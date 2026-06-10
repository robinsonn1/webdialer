# Twilio Web Dialer Sandbox

A lightweight web-based telephony client built with Python Flask and the Twilio Voice WebRTC SDK (v2.x). Execute outbound calls directly from a browser, interact with IVR menus via live DTMF, sync contacts to HubSpot CRM, and track full call telemetry including Call SIDs.
https://github.com/robinsonn1/webdialer/blob/main/Screenshots/Web_dialer_her.png
## Features

- **Outbound WebRTC Calls**: Dial any E.164 number directly from the browser using Twilio's Voice SDK.
- **Call SID Tracking**: Every call's Twilio-assigned SID is captured and displayed in the status panel, telemetry table, and debug console.
- **E.164 Validation**: Real-time format checking with country detection as you type.
- **Live DTMF Engine**: Send keypad digits over active calls for IVR navigation; logged in the session table.
- **Mute/Unmute Control**: Toggle microphone audio mid-call from the interface.
- **HubSpot CRM Sync**: Contacts are automatically created or matched by phone number on every call. Contact IDs link directly to the HubSpot record.
- **Multi-Zone Clocks**: Live PST, CT, and Bogotá time displayed in the header.
- **Debug Console**: Real-time telemetry stream with color-coded log levels.

## Requirements

- Python 3.8+
- A Twilio account with:
  - A verified phone number
  - An API Key + Secret pair
  - A TwiML App configured with your ngrok webhook URL
- (Optional) A HubSpot account with a Private App access token

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/robinsonn1/webdialer.git
cd webdialer
```

### 2. Create and activate a virtual environment

```bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate

# Windows PowerShell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_API_KEY=SKxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_API_SECRET=your_api_secret
TWILIO_TWIML_APP_SID=APxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_PHONE_NUMBER=+1xxxxxxxxxx

# Optional — omit to disable HubSpot integration
HUBSPOT_ACCESS_TOKEN=your_hubspot_private_app_token
```

### 5. Start the app

```bash
python app.py
```

### 6. Expose via ngrok

```bash
ngrok http 8080
```

Copy the ngrok HTTPS URL and set it as the Voice webhook in your Twilio TwiML App:

```
https://your-ngrok-url.ngrok.io/voice
```

## API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/` | Serve the web dialer UI |
| GET | `/token` | Issue a Twilio Access Token for the browser client |
| POST | `/voice` | TwiML webhook — handles outbound call routing and CRM sync |
| POST | `/dtmf-log` | Log a DTMF digit sent during a live call |
| GET | `/logs` | Return the in-memory call history (JSON) |
| GET | `/hs-debug` | Smoke-test the HubSpot API connection |

## Call SID

Each outbound call generates a unique `CallSid` (e.g. `CAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`) assigned by Twilio. This ID is:

- Captured server-side from the `/voice` webhook POST body
- Read client-side from `connection.parameters.CallSid` on call accept
- Displayed in the left panel status block and the telemetry table
- Logged to the debug console as a `[SID]` entry
- Useful for looking up call recordings, logs, and events in the Twilio Console

## Notes

- The `.env` file is excluded from version control via `.gitignore` — never commit credentials.
- `node_modules/` should also be in `.gitignore` and not committed to the repository.
- Call history is stored in memory and resets on server restart.
