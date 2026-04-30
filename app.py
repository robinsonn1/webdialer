import os
from flask import Flask, render_template, request, jsonify
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
        # Save to log
        call_history.append({"to": to_number, "status": "Initiated"})
        
        # Dial with recording enabled
        dial = response.dial(caller_id=TWILIO_NUMBER, record='record-from-answer')
        dial.number(to_number)
    else:
        response.say("No number provided.")
        
    return str(response), 200, {'Content-Type': 'text/xml'}

@app.route("/logs", methods=['GET'])
def get_logs():
    return jsonify(call_history)

if __name__ == "__main__":
    app.run(debug=True, port=5000)