import logging

from granoclient.loader import Loader

from kompromatron.core import grano
from kompromatron.loaders.util import read_json

SOURCE_URL = 'http://www.bundestag.de/dokumente/lobbyliste/lobbylisteaktuell.pdf'
log = logging.getLogger(__name__)


def load_verband(loader, verband):
    log.info('Verband: %s', verband['name'])

    org = loader.make_entity(['organisation', 'lobbyorganisation',
                                'contact', 'address'])

    org.set('name', verband['name'])
    addr = [l for l in verband['locations'] if not l.get('parliament')]
    if addr:
        addr = addr[0]
        city = addr['address'].splitlines()[-1]
        try:
            plz, city = city.split(' ', 1)
        except ValueError:
            pass
        else:
            org.set('seat_city', city)
            org.set('city', city)
            org.set('postcode', plz)

        org.set('street', '\n'.join(addr['address'].splitlines()[:-1]))
        org.set('email', addr.get('email'))
        org.set('website', addr.get('web'))
        org.set('fax', addr.get('fax'))
        org.set('phone', addr.get('phone'))

    org.set('interestarea', verband['interestarea'])
    org.set('membercount', verband['membercount'])
    org.set('organisationcount', verband.get('organizationcount', 0))
    org.save()

    board_members = []
    representatives = []

    for member in verband['board']:
        p = loader.make_entity(['person'])
        p.set('name', member[1])
        try:
            first, last = member[1].split(' ', 1)
            p.set('first_name', first)
            p.set('last_name', last)
        except ValueError:
            pass
        if member[0]:
            p.set('title', member[0])
        role = None
        if len(member) > 2:
            role = member[2]
        p.save()
        board_members.append((p, role))

    for rep in verband['representatives']:
        if rep == '@board':
            representatives.extend(board_members)
            continue
        p = loader.make_entity(['person'])
        p.set('name', rep[1])
        if rep[0]:
            p.set('title', rep[0])
        role = None
        if len(rep) > 2:
            role = rep[2]
        p.save()
        representatives.append((p, role))

    for member in board_members:
        s = loader.make_relation('board_member', member[0], org)
        if member[1]:
            s.set('board_role', member[1])
        s.save()

    for rep in representatives:
        s = loader.make_relation('org_representative', rep[0], org)
        s.save()


def load_verbaende():
    loader = Loader(grano, source_url=SOURCE_URL)

    orgs = read_json('data/verbaende.json')
    for org in orgs:
        try:
            load_verband(loader, org)
        except Exception as e:
            log.error('Failed loading with %s at %s', e, org)
