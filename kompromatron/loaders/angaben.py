import logging

from granoclient.loader import Loader

from kompromatron.core import grano, NotFound
from kompromatron.loaders.util import read_json

SOURCE_URL = 'http://www.bundestag.de/service/glossar/R/rechenschaftsberichte.html'
log = logging.getLogger(__name__)

MDBS = {}

def load_angabe(loader, angabe, bt):
    source_url = angabe.pop('source_url')
    fp = angabe.pop('fingerprint')
    if fp is None:
        return
    log.info('MdB: %s', fp)
    if fp not in MDBS:
        mdb = loader.make_entity(['person'], source_url=source_url)
        mdb.set('name', fp.strip())
        mdb.set('first_name', angabe.pop('vorname'))
        mdb.set('last_name', angabe.pop('nachname'))
        mdb.set('title', angabe.pop('titel'))
        mdb.set('nobility', angabe.pop('adelstitel'))
        mdb.set('religion', angabe.pop('religion'))
        mdb.set('biography', angabe.pop('bio'))
        mdb.set('gender', angabe.pop('geschlecht'))
        mdb.set('dob', angabe.pop('geburtsdatum'))
        mdb.set('twitter_url', angabe.pop('twitter_url'))
        mdb.set('facebook_url', angabe.pop('facebook_url'))
        mdb.set('homepage_url', angabe.pop('homepage_url'))
        mdb.set('occupation', angabe.pop('beruf'))
        mdb.set('children', angabe.pop('kinder'))
        mdb.set('origin_state', angabe.pop('land'))
        mdb.set('origin_city', angabe.pop('ort'))
        mdb.set('foto_url', angabe.pop('foto_url'))
        mdb.save()
        MDBS[fp] = mdb
    mdb = MDBS[fp]

    party = loader.make_entity(['party'], source_url=source_url)
    party.set('name', angabe.get('partei'))
    party.set('acronym', angabe.pop('partei'))
    party.save()

    pm = loader.make_relation('party_member', mdb, party)
    pm.save()

    man = loader.make_relation('bt_mandate', mdb, bt)
    man.set('mdb_id', angabe.pop('mdb_id'))
    man.set('faction', angabe.pop('fraktion'))
    man.set('constituency', angabe.pop('wk_nummer'))
    man.save()

    if angabe.get('client_name') and len(angabe.get('client_name').strip()):
        org = loader.make_entity(['organisation', 'address'], source_url=source_url)
        org.set('name', angabe.pop('client_name'))
        org.set('city', angabe.pop('client_city'))
        org.save()

        si = loader.make_relation('side_income', mdb, org)
        si.set('level', angabe.pop('level'))
        si.set('section', angabe.pop('section'))
        si.set('service', angabe.pop('service'))
        si.save()

    #from pprint import pprint
    #pprint(angabe)
    #print [angabe.get('client_name'), angabe.get('client_city')]


def load_angaben():
    loader = Loader(grano, source_url=SOURCE_URL)

    bt = loader.make_entity(['public_body'])
    bt.set('name', '17. Deutscher Bundestag')
    bt.save()

    angaben = read_json('data/angaben.json')
    for angabe in angaben.get('results'):
        load_angabe(loader, angabe, bt)
