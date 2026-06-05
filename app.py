import os
from flask import Flask, render_template, request, jsonify, Response
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VoiceGrant
from twilio.twiml.voice_response import VoiceResponse
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Credentials from .env
ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
API_KEY = os.getenv('TWILIO_API_KEY')
API_SECRET = os.getenv('TWILIO_API_SECRET')
TWIML_APP_SID = os.getenv('TWILIO_TWIML_APP_SID')
TWILIO_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

# Simple in-memory call log
call_history = []

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/token", methods=['GET'])
def get_token():
    try:
        identity = 'web_user_rnavarro'
        token = AccessToken(ACCOUNT_SID, API_KEY, API_SECRET, identity=identity)
        
        # Outgoing permission
        voice_grant = VoiceGrant(outgoing_application_sid=TWIML_APP_SID)
        token.add_grant(voice_grant)
        return jsonify(token=token.to_jwt())
    except Exception as e:
        return jsonify(error=str(e)), 500

@app.route("/voice", methods=['POST'])
def voice():
    """Handles Outgoing calls with Recording enabled."""
    response = VoiceResponse()
    to_number = request.form.get('To')

    if to_number:
        # Save to log with placeholder string for DTMF telemetry
        call_history.append({"to": to_number, "status": "Initiated", "dtmf": ""})
        
        # Dial with recording enabled
        dial = response.dial(caller_id=TWILIO_NUMBER, record='record-from-answer')
        dial.number(to_number)
    else:
        response.say("No number provided.")
        
    # Return cleanly enforcing XML mimetype & explicitly inject ngrok bypass headers
    res = Response(str(response), mimetype='text/xml')
    res.headers["ngrok-skip-browser-warning"] = "true"
    return res

@app.route("/dtmf-log", methods=['POST'])
def log_dtmf():
    """Appends live transmitted DTMF digits to the active transaction history block."""
    data = request.json or {}
    digit = data.get("digit")
    
    if digit and call_history:
        latest_call = call_history[-1]
        if not latest_call.get("dtmf"):
            latest_call["dtmf"] = str(digit)
        else:
            latest_call["dtmf"] += f", {digit}"
        return jsonify(success=True)
    return jsonify(success=False), 400

@app.route("/logs", methods=['GET'])
def get_logs():
    return jsonify(call_history)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8080)