from flask import Flask, render_template, redirect, url_for
from flask.ext.bootstrap import Bootstrap
from os import path


def create_app():
    app = Flask(__name__, static_folder='tmpl')

    app.config.from_object('app.defaults')
    if path.exists('settings.py'):
        app.config.from_object('settings.py')
        
    import extensions
    extensions.init_app(app)
    


    @app.route('/')
    def homepage(): 
        return redirect(url_for('frontend.index'))
    return app