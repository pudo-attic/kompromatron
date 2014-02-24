from kompromatron.core import freezer, grano


@freezer.register_generator
def entity():
    for entity in grano.entities:
        yield {'id': entity.id}


@freezer.register_generator
def relation():
    for relation in grano.relation:
        yield {'id': relation.id}


