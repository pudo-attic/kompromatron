from flask import request

from kompromatron.core import app

@app.route('/')
def index():
    return 'kompromatron'
