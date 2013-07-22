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


# Voice Request URL
@app.route('/voice', methods=['GET', 'POST'])
def voice():
    response = twiml.Response()
    response.play("/static/sounds/nospoilersallowed.mp3")
    response.say("We are always listening.")
    response.record()
    return str(response)


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
    app.run(host='0.0.0.0', port=port)
