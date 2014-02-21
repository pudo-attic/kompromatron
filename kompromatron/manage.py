from flask.ext.script import Manager
from flask.ext.assets import ManageAssets

from kompromatron.core import assets
from kompromatron.web import app
from kompromatron.loaders.schema import load_schemata
from kompromatron.loaders.angaben import load_angaben
from kompromatron.loaders.spenden import load_spenden
from kompromatron.loaders.verbaende import load_verbaende

manager = Manager(app)
manager.add_command("assets", ManageAssets(assets))


@manager.command
def load():
    """ Load all the datas. """
    load_schemata()
    load_angaben()
    load_spenden()
    load_verbaende()


if __name__ == "__main__":
    manager.run()
