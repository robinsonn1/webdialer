# Twilio Web Dialer Sandbox

An active lightweight web-based telephony client built with Python Flask and the Twilio Voice WebRTC SDK (v2.x). This sandbox allows developers to execute outbound calls directly from a browser, interact with interactive voice response (IVR) phone menus, track logging diagnostics, and handle automated tunneling rules smoothly.

## System Architecture

The application exposes a local web architecture that authenticates browser clients via an access control token. Outbound requests travel through standard WebRTC protocols toward Twilio's communications framework gateway, fetching structural execution layout paths via an active proxy tunnel webhook endpoint.

## Features Checklist
- **E.164 String Checking**: Evaluates destination phone layouts in real time.
- **Live Call Telemetry**: Prints logs containing connection markers, network handshake confirmations, and execution parameters.
- **Mute Control Block**: Suspends microphone audio streams directly from the application interface.
- **Live DTMF Engine**: Transmits menu digits over active call lines and updates log history automatically.
- **Integrated Clock Module**: Tracks system time metrics across several international time zones simultaneously.

## Installation Requirements
- Python 3.8+
- An active Twilio Account containing a verified Twilio Phone Number, API Keys, and an active TwiML App registration configuration ID.

## Setup Instructions

1. **Clone project source files and move inside the root path directory**:
   ```bash
   git clone [https://github.com/robinsonn1/webdialer.git](https://github.com/robinsonn1/webdialer.git)
   cd webdialer

## Local Setup
1. **Install Requirements:**
   ```bash
   pip install flask twilio python-dotenv

   Environment Variables (.env):

TWILIO_ACCOUNT_SID

TWILIO_AUTH_TOKEN

TWILIO_API_KEY

TWILIO_API_SECRET

TWILIO_TWIML_APP_SID

TWILIO_PHONE_NUMBER

Run App:

Bash
python app.py
Ngrok:

Bash
ngrok http 5000