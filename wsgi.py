from app import create_app

def app_factory(global_config, **local_config):
    app = create_app()
    return app.wsgi_app