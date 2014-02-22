from kompromatron.core import app
from kompromatron.views.base import base

# app.register_blueprint(entities)
# app.register_blueprint(relations)
app.register_blueprint(base)
