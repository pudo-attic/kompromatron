from flask import Blueprint, render_template, request
# from flask import redirect

from kompromatron.core import grano


base = Blueprint('base', __name__, static_folder='../static', template_folder='../templates')


@base.route('/')
def index():
    return render_template('index.html')


@base.route('/entities/<id>')
def entity(id):
    entity = grano.entities.by_id(id)
    return render_template('entity.html', entity=entity)


@base.route('/browse')
def browse():
    params = {
        'q': request.args.get('q', ''),
        'offset': request.args.get('offset', 0),
        'project': grano.slug
    }
    s, results = grano.client.get('/entities', params=params)
    print results.get('results')[0]
    return render_template('browse.html', results=results)
