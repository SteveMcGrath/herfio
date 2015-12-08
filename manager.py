#!/usr/bin/env python
from app import create_app
from flask.ext.script import Manager
from flask.ext.migrate import MigrateCommand
from app.extensions import db


app = create_app()
manager = Manager(app)
manager.add_command('db', MigrateCommand)

@manager.command
def list_routes():
    import urllib
    from flask import url_for
    output = []
    for rule in app.url_map.iter_rules():

        options = {}
        for arg in rule.arguments:
            options[arg] = "[{0}]".format(arg)

        methods = ','.join(rule.methods)
        url = url_for(rule.endpoint, **options)
        line = urllib.unquote("{:50s} {:20s} {}".format(rule.endpoint, methods, url))
        output.append(line)

    for line in sorted(output):
        print line

# These are the parsers that we will be using...
from app.parsers import parsers

@manager.command
def update():
    for parser in parsers:
        parsers[parser].run()

@manager.command
def parser(name):
    parsers[name].run()

@manager.command
def close(name, state=0):
    parsers[name].close_auctions(bool(state))

# This should almost never need to be run.  As it will surely piss off the
# auction sites, it's commented out unless really needed.
#@manager.command
#def price_cleanup():
#    for parser in parsers:
#        parsers[parser].run(finish_state=True, get_new_listings=False)


if __name__ == '__main__':
    manager.run()
