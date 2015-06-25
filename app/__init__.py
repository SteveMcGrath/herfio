from flask.ext.bootstrap import Bootstrap
import os


def create_app():
    '''App Builder'''
    from views import app

    # Pull in the configuration.
    app.config.from_object('app.defaults')
    #settings_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'settings.py')
    #if os.path.exists(settings_file):
    #    app.config.from_object(settings_file)

    # Initialize the extensions and return the resultant app object.
    import extensions
    extensions.init_app(app)
    return app