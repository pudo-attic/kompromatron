from flask import Blueprint, render_template, request
# from flask import redirect

from kompromatron.core import grano, app


base = app #Blueprint('base', __name__, static_folder='../static', template_folder='../templates')
SCHEMA_CACHE = {}


def get_schema(name):
    if not name in SCHEMA_CACHE:
        SCHEMA_CACHE[name] = grano.schemata.by_name(name)
    return SCHEMA_CACHE[name]


def get_attribute(schemata, name):
    if not isinstance(schemata, list):
        schemata = [schemata]
    for schema in schemata:
        schema = get_schema(schema.get('name'))
        for attribute in schema.attributes:
            if attribute.get('name') == name:
                return attribute

@app.context_processor
def inject():
    return dict(get_schema=get_schema, get_attribute=get_attribute)


@base.route('/')
@base.route('/index.html')
def index():
    return render_template('index.html')


@base.route('/about.html')
def about():
    return render_template('about.html')


@base.route('/entities/<id>.html')
def entity(id):
    entity = grano.entities.by_id(id)
    schemata = entity.schemata
    return render_template('entity.html', entity=entity,
        schemata=schemata, query=entity.properties.get('name', {}).get('value'))


@base.route('/relations/<id>.html')
def relation(id):
    relation = grano.relations.by_id(id)
    return render_template('relation.html', relation=relation)


@base.route('/browse.html')
def browse():
    params = {
        'q': request.args.get('q', ''),
        'offset': request.args.get('offset', 0),
        'project': grano.slug
    }
    s, results = grano.client.get('/entities', params=params)
    #print results.get('results')[0]
    return render_template('browse.html', results=results,
        query=params.get('q'))
