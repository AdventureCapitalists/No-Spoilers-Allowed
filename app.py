from functools import wraps
import os
import signal

from flask import Flask
from flask import Response
from flask import current_app
from flask import render_template
from flask import request
from flask import url_for

from twilio import twiml
from twilio.util import RequestValidator
from twilio.util import TwilioCapability
from urlobject import URLObject


# Declare and configure application
app = Flask(__name__, static_url_path='/static')
app.config.from_pyfile('local_settings.py')


def twilio_secure(func):
    """Wrap a view function to ensure that every request comes from Twilio."""
    @wraps(func)
    def wrapper(*a, **kw):
        if validate_twilio_request():
            return func(*a, **kw)
        return Response("Not a valid Twilio request", status=403)
    return wrapper


# Voice Request URL
@app.route('/voice', methods=['GET', 'POST'])
@twilio_secure
def voice():
    response = twiml.Response()
    response.play("/static/sounds/nospoilersallowed.mp3")
    response.say("We are always listening.")
    response.record()
    return str(response)


def validate_twilio_request():
    """Ensure a request is coming from Twilio by checking the signature."""
    validator = RequestValidator(current_app.config['TWILIO_AUTH_TOKEN'])
    if 'X-Twilio-Signature' not in request.headers:
        return False
    signature = request.headers['X-Twilio-Signature']
    if 'CallSid' in request.form:
        # See: http://www.twilio.com/docs/security#notes
        url = URLObject(url_for('.voice', _external=True)).without_auth()
        if request.is_secure:
            url = url.without_port()
    elif 'SmsSid' in request.form:
        url = url_for('.sms', _external=True)
    else:
        return False
    return validator.validate(url, request.form, signature)


# Handles SIGTERM so that we don't get an error when Heroku wants or needs to
# restart the dyno
def graceful_shutdown(signum, frame):
    exit()

signal.signal(signal.SIGTERM, graceful_shutdown)


# If PORT not specified by environment, assume development config.
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    if port == 5000:
        app.debug = True
    app.debug = True
    app.run(host='0.0.0.0', port=port)
