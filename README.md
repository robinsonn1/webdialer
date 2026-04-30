# Twilio Web Dialer

A browser-based VoIP phone built with Python (Flask) and Twilio Voice SDK.

<img width="812" height="557" alt="image" src="https://github.com/user-attachments/assets/e3a42de0-9b27-45fd-94a0-10099dd7416b" />


## Features
- Outgoing calls via WebRTC.
- Automated Call Recording.
- Live Mute/Unmute toggle.
- Session-based Call History log.

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
