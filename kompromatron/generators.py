from kompromatron.core import freezer, grano


@freezer.register_generator
def entity():
    for entity in grano.entities:
        print 'Generate Entity: %s' % entity.id
        yield {'id': entity.id}


@freezer.register_generator
def relation():
    for relation in grano.relation:
        print 'Generate Relation: %s' % relation.id
        yield {'id': relation.id}


