from flask import request, jsonify, g, abort, url_for, current_app
from . import api
from ..models import Work
from .. import db, cache

@api.route('/works/')
@cache.cached(timeout=120)
def get_works():
    page = request.args.get('page', 1, type=int)
    pagination = Work.query.paginate(page, per_page=current_app.config['CSRANKINGS_WORKS_PER_PAGE'], error_out=False)

    all_posts = pagination.items
    posts = []
    for post in all_posts:
        if post.matched:
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