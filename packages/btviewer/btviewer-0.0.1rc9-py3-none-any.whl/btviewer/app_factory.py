"""
Flask application factory
"""
import os
from pathlib import Path
from typing import Union

import flask


def create_app(root_directory: Union[Path, str] = None, **kwargs) -> flask.Flask:
    """
    Build the Flask app instance

    This function is a Flask application factory
    https://flask.palletsprojects.com/en/3.0.x/patterns/appfactories/

    :param root_directory: The base directory for image capture session data.
    :param kwargs: keyword arguments for the Flask app
    """
    app = flask.Flask(__name__, **kwargs)
    root_directory = Path(root_directory or os.getenv('ROOT_DIRECTORY', '.')).absolute()
    app.config.update(dict(
        ROOT_DIRECTORY=str(root_directory),
    ))
    register_blueprints(app)

    app.after_request(set_headers)

    return app


def set_headers(response: flask.Response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


def register_blueprints(app: flask.Flask):
    """
    Add the blueprints to the flask app
    https://flask.palletsprojects.com/en/3.0.x/blueprints/
    """

    import btviewer.blueprints.session.views
    import btviewer.blueprints.label.views
    import btviewer.blueprints.photo.views

    app.register_blueprint(btviewer.blueprints.photo.views.blueprint)
    app.register_blueprint(btviewer.blueprints.label.views.blueprint)
    app.register_blueprint(btviewer.blueprints.session.views.blueprint)
