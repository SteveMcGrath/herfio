from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.bootstrap import Bootstrap
from flask.ext.migrate import Migrate
from flask.ext.script import Manager
from wtforms_alchemy import model_form_factory
from flask.ext.wtf import Form


migrate = Migrate()
db = SQLAlchemy()


def init_app(app):
    Bootstrap(app)
    db.init_app(app)
    migrate.init_app(app, db)