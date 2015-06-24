#!/usr/bin/env python
from app import create_app
from flask.ext.script import Manager
from flask.ext.migrate import MigrateCommand
from app.extensions import db


app = create_app()
manager = Manager(app)
manager.add_command('db', MigrateCommand)

# These are the parsers that we will be using...
from app.parsers import parsers

@manager.command
def update():
    for parser in parsers:
        print 'Starting the %s parser...' % parser
        parsers[parser].run()


if __name__ == '__main__':
    manager.run()