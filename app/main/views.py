from flask import render_template
from . import main
from .. import cache

@cache.cached(timeout=60*2)
@main.route('/index/')
def main():
    return render_template('index.html')