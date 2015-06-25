from flask.ext.bootstrap import Bootstrap
from os import path


def create_app():
    '''App Builder'''
    from views import app

    # Pull in the configuration.
    app.config.from_object('app.defaults')
    if path.exists('settings.py'):
        app.config.from_object('settings.py')

    # Initialize the extensions and return the resultant app object.
    import extensions
    extensions.init_app(app)
    return app

def app_factory(global_config, **local_config):
    app = create_app()
    return app.wsgi_app