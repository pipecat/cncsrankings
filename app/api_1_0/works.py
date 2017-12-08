import json
from flask import request, jsonify, g, abort, url_for, current_app, Response, send_file, current_app
from . import api
from ..models import Work
from .. import db, cache

@api.route('/get/works.json')
@cache.cached(timeout=120)
def get_works():
    '''
    page = request.args.get('page', 1, type=int)
    pagination = Work.query.paginate(page, per_page=current_app.config['CSRANKINGS_WORKS_PER_PAGE'], error_out=False)

    with open('app/filters.json', 'r') as f:
        filters = json.loads(f.read())

    all_posts = pagination.items
    posts = []
    for post in all_posts:
        keys = post.key.split('/')
        filter = keys[0] + '/' + keys[1]
        if post.matched and filter in filters:
            posts.append(post)

    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_works', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_works', page=page+1, _external=True)
    return jsonify({
        'posts': [post.to_json() for post in posts ],
        'prev': prev,
        'next': next,
        'count': pagination.total
        })
    '''
    #works = file('app/static/works.json')
    #res = Response(works, mimetype="application/json")
    return current_app.send_static_file('works.json')
    


@api.route('/send_person', methods=['POST'])
def recieve_person():
    with open('persons.json', 'r') as f:
        persons = json.loads(f.read())
    print request.get_data(), len(request.get_data())
    data = json.loads(request.get_data())
    persons.append(data)
    print persons
    with open('persons.json', 'w') as f:
        f.write(json.dumps(persons))

    return 'OK!'