#!/usr/bin/venv python

import os

if os.path.exists('.venv'):
    print('Importing enviroment from venv')
    for line in open('.venv'):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[var[0]] = var[1]


import os
from app import create_app, db, cache
from app.models import Work, MatchedWork, Generate_all
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand


app = create_app('producton')
manager = Manager(app)
migrate = Migrate(app, db)

def make_shell_context():
    return dict(Work=Work, db=db, MatchedWork=MatchedWork, Generate_all=Generate_all, cache=cache, works = Work.query.all())

manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()