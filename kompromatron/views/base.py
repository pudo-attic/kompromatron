from flask import Blueprint, render_template
# from flask import redirect

# from grano.core import url_for
# from grano.logic.searcher import search_entities


base = Blueprint('base', __name__, static_folder='../static', template_folder='../templates')


@base.route('/')
def index():
    # searcher = search_entities({})
    # searcher.add_facet('schemata.name', 20)
    # schemata_facet = facet_schema_list(Entity, searcher.get_facet('schemata.name'))
    return render_template('index.html')
