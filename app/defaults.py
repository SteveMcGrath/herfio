import os

CSRF_ENABLED = True
DEBUG = True
TESTING = True
SECRET_KEY = 'This is the default key INSECURE!'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'database.db')
SQLALCHEMY_MIGRATE_REPO = 'db_repository'
SERVER_NAME = 'localhost:5000'