import logging

from granoclient.loader import Loader
from unicodecsv import DictReader

from kompromatron.core import grano, NotFound
from kompromatron.loaders.util import read_file

SOURCE_URL = 'http://www.bundestag.de/service/glossar/R/rechenschaftsberichte.html'
log = logging.getLogger(__name__)

PARTIES = {}

def load_spende(loader, spende):
    log.info('Parteispende: %s an %s', spende['spender_name'], spende['partei_name'])
    
    if spende.get('partei_name') not in PARTIES:
        party = loader.make_entity(['party'])
        party.set('name', spende.get('partei_name'))
        if 'partei_acronym' in spende:
            party.set('acronym', spende.pop('partei_acronym'))
        party.save()
        PARTIES[spende.get('partei_name')] = party
    party = PARTIES[spende.get('partei_name')]

    typ = []
    if 'spender_typ' in spende:
        typ.append('person' if spende.pop('spender_typ', 'org') == 'nat' else 'organisation')
    spender = loader.make_entity(['address'] + typ)
    spender.set('name', spende.pop('spender_name'))
    spender.set('street', spende.pop('spender_strasse'))
    spender.set('postcode', spende.pop('spender_plz'))
    spender.set('city', spende.pop('spender_stadt'))
    spender.save()

    s = loader.make_relation('party_donation', spender, party)
    s.unique('internal_id')
    s.set('internal_id', spende.pop('id'))
    s.set('year', spende.pop('jahr'))
    s.set('amount', spende.pop('betrag_eur'))
    s.save()


def load_spenden():
    for file_name in ['data/spenden_2011.csv', 'data/spenden.csv']:
        loader = Loader(grano, source_url=SOURCE_URL)

        fh = read_file(file_name)
        reader = DictReader(fh)
        for row in reader:
            load_spende(loader, row)

