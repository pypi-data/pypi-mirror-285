from pathlib import Path

import flask

from .models import Session

app: flask.Flask = flask.current_app

blueprint = flask.Blueprint('session', __name__, url_prefix='/sessions')


@blueprint.route("/")
@blueprint.route("/<path:relative_path>")
def list_(relative_path: str = None):
    """
    List directory contents of _any_ data subdirectory

    <root_directory>/<session>/<set>/<device id>/<camera id>/<timestamp>_<photo id>.np

    This endpoint returns a list of strings, each is the path of that directory or photo file.

    Example: GET /sessions/2020-01-01/set_A/device_1
    [
      "2020-01-01/set_A/device_1/camera_1",
      "2020-01-01/set_A/device_1/camera_2"
    ]
    """

    # Get the specified directory
    root_directory = Session.root_directory()
    relative_path = Path(relative_path or '')
    path: Path = root_directory.joinpath(relative_path)

    # Are we in a camera directory that contains photos?
    # (i.e. Are we at least four subdirectories deep in the file structure?)
    if len(relative_path.parents) >= 4:
        # Get photo files
        paths = path.glob("*.np")
    else:
        # Get subdirectory names
        paths = (_path for _path in path.iterdir() if _path.is_dir())

    # Get the full path relative to the root directory
    full_paths = tuple(str(path.relative_to(root_directory).as_posix()) for path in paths)
    return flask.jsonify(full_paths)
