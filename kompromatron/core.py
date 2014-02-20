from flask import Flask, url_for as _url_for
from flask.ext.assets import Environment

from kompromatron import default_settings

app = Flask(__name__)
app.config.from_object(default_settings)
app.config.from_envvar('KOMPROMATRON_SETTINGS', silent=True)

assets = Environment(app)
