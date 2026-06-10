import os
from flask import Flask, render_template, request, jsonify, Response
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VoiceGrant
from twilio.twiml.voice_response import VoiceResponse
from dotenv import load_dotenv

# HubSpot
from hubspot import HubSpot
from hubspot.crm.contacts import SimplePublicObjectInputForCreate, PublicObjectSearchRequest
from hubspot.crm.contacts.exceptions import ApiException

load_dotenv()
app = Flask(__name__)

# Twilio credentials
ACCOUNT_SID   = os.getenv('TWILIO_ACCOUNT_SID')
API_KEY       = os.getenv('TWILIO_API_KEY')
API_SECRET    = os.getenv('TWILIO_API_SECRET')
TWIML_APP_SID = os.getenv('TWILIO_TWIML_APP_SID')
TWILIO_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

# HubSpot client
HUBSPOT_TOKEN = os.getenv('HUBSPOT_ACCESS_TOKEN')
hs = HubSpot(access_token=HUBSPOT_TOKEN) if HUBSPOT_TOKEN else None

# In-memory call log
call_history = []


# ── HubSpot helper ─────────────────────────────────────────────────────────────

def sync_contact_to_hubspot(phone_number: str) -> dict:
    """
    Create or find a HubSpot contact by phone number.
    Returns { hs_status, hs_contact_id, hs_log } — hs_log is shown in the browser console.
    """
    if not hs:
        msg = "HUBSPOT_ACCESS_TOKEN missing from .env — integration skipped."
        print(f"[HubSpot] {msg}")
        return {"hs_status": "no-token", "hs_contact_id": None, "hs_log": msg}

    print(f"[HubSpot] Searching for existing contact with phone: {phone_number}")
    try:
        search_req = PublicObjectSearchRequest(
            filter_groups=[{
                "filters": [{
                    "value": phone_number,
                    "propertyName": "phone",
                    "operator": "EQ"
                }]
            }],
            properties=["phone", "firstname", "lastname"]
        )
        results = hs.crm.contacts.search_api.do_search(
            public_object_search_request=search_req
        )

        if results.total > 0:
            contact_id = results.results[0].id
            msg = f"Contact already exists — ID: {contact_id}"
            print(f"[HubSpot] {msg}")
            return {"hs_status": "existing", "hs_contact_id": contact_id, "hs_log": msg}

        # Create new contact
        print(f"[HubSpot] No existing contact found — creating new contact...")
        new_contact = hs.crm.contacts.basic_api.create(
            simple_public_object_input_for_create=SimplePublicObjectInputForCreate(
                properties={
                    "phone":     phone_number,
                    "firstname": "Unknown",
                    "lastname":  "Caller"
                }
            )
        )
        msg = f"New contact created — ID: {new_contact.id}"
        print(f"[HubSpot] {msg}")
        return {"hs_status": "created", "hs_contact_id": new_contact.id, "hs_log": msg}

    except ApiException as e:
        msg = f"API error {e.status}: {e.reason}"
        print(f"[HubSpot] {msg}\nBody: {e.body}")
        return {"hs_status": f"error:{e.status}", "hs_contact_id": None, "hs_log": msg}
    except Exception as e:
        msg = f"Unexpected error: {str(e)}"
        print(f"[HubSpot] {msg}")
        return {"hs_status": "error", "hs_contact_id": None, "hs_log": msg}


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/token", methods=['GET'])
def get_token():
    try:
        identity = 'web_user_rnavarro'
        token = AccessToken(ACCOUNT_SID, API_KEY, API_SECRET, identity=identity)
        voice_grant = VoiceGrant(outgoing_application_sid=TWIML_APP_SID)
        token.add_grant(voice_grant)
        return jsonify(token=token.to_jwt())
    except Exception as e:
        return jsonify(error=str(e)), 500


@app.route("/voice", methods=['POST'])
def voice():
    """Handles outgoing calls with recording + HubSpot contact sync."""
    response  = VoiceResponse()
    to_number = request.form.get('To')

    if to_number:
        hs_result = sync_contact_to_hubspot(to_number)

        call_history.append({
            "to":            to_number,
            "status":        "Initiated",
            "dtmf":          "",
            "hs_status":     hs_result["hs_status"],
            "hs_contact_id": hs_result["hs_contact_id"],
            "hs_log":        hs_result["hs_log"],
        })

        dial = response.dial(caller_id=TWILIO_NUMBER, record='record-from-answer')
        dial.number(to_number)
    else:
        response.say("No number provided.")

    res = Response(str(response), mimetype='text/xml')
    res.headers["ngrok-skip-browser-warning"] = "true"
    return res


@app.route("/dtmf-log", methods=['POST'])
def log_dtmf():
    data  = request.json or {}
    digit = data.get("digit")
    if digit and call_history:
        latest = call_history[-1]
        latest["dtmf"] = latest["dtmf"] + f", {digit}" if latest.get("dtmf") else str(digit)
        return jsonify(success=True)
    return jsonify(success=False), 400


@app.route("/logs", methods=['GET'])
def get_logs():
    return jsonify(call_history)


@app.route("/hs-debug", methods=['GET'])
def hs_debug():
    """Smoke-test the HubSpot connection — call from browser to verify credentials."""
    if not hs:
        return jsonify(ok=False, error="HUBSPOT_ACCESS_TOKEN not set in .env"), 500
    try:
        # Fetch at most 1 contact just to confirm auth works
        result = hs.crm.contacts.basic_api.get_page(limit=1)
        return jsonify(ok=True, message="HubSpot connection OK", contacts_found=len(result.results))
    except ApiException as e:
        return jsonify(ok=False, error=f"API error {e.status}: {e.reason}", body=e.body), 500
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 500


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8080)