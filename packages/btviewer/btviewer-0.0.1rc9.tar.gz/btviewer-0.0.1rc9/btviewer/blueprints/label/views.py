from http import HTTPStatus

import flask

from btviewer.blueprints.photo.model import Photo

app: flask.Flask = flask.current_app
blueprint = flask.Blueprint("label", __name__, url_prefix="/labels")


@blueprint.route("/detail", methods=["GET"])
def detail():
    """
    Get all the tags associated with this image

    Usage:
    /label/detail?path=1970-01-01/set_A/device_1234/camera_1/20200101_094359.123456_000002.np

    :returns: List of labels
    [
      {"confidence": "Unsure", "x": 321, "y": 789},
      {"confidence": "Sure", "x": 123, "y": 6564},
      {"confidence": "Unsure", "x": 456, "y": 789}
    ]
    """
    photo = Photo(flask.request.args["path"])
    return flask.jsonify(photo.labels)


@blueprint.route("/create", methods=["POST"])
def create():
    """
    Create new labels

    The front end will send a POST request to create the labels with an
    array of label information like so:

    POST
    http://localhost:5000/labels/create?path=1970-01-01/set_A/device_1234/camera_1/20200101_094359.123456_000002.np

    [
        {
          "x": 123,
          "y": 456,
          "confident": true,
          "label": "not the bees!"
        },
        {
          "x": 123,
          "y": 456,
          "confident": true,
          "label": "To be, or not to be."
        }
    ]
    """

    # Load the selected image
    photo_path = flask.request.args["path"]
    photo = Photo(photo_path)

    # Get the label data from the request
    source = flask.request.args["source"]
    version = flask.request.args["version"]
    labels = flask.request.json

    # Create the labels
    label_path = photo.add_labels(labels, source=source, version=version)

    # Return a success response
    return flask.jsonify(dict(label_path=str(label_path))), HTTPStatus.CREATED


@blueprint.route("/delete", methods=["DELETE"])
def delete():
    """
    Delete all the labels on a photo by deleting the file
    """

    # Load the selected image
    photo_path = flask.request.args["path"]
    photo = Photo(photo_path)

    # Delete all photos from this course
    source = flask.request.args["source"]
    photo.delete_labels(source)

    return '', HTTPStatus.NO_CONTENT


# the modify route is for deleting single label as the methods used is post, not delete compared to the delete all.
@blueprint.route("/modify", methods=["POST"])
def modify():
    """
    Delete single label on a photo
    """

    # Load the selected image
    photo = Photo(flask.request.args["path"])
    source = flask.request.args["source"]
    x = int(flask.request.args["x"])
    y = int(flask.request.args["y"])

    photo.delete_labels(source, x, y)

    return '', HTTPStatus.NO_CONTENT


@blueprint.route("/annotate", methods=["POST"])  # the annotate route is for annotate existing single label
def annotate():
    """
    annotate an existing label on a photo
    """

    # Load the selected image
    photo = Photo(flask.request.args["path"])
    source = flask.request.args["source"]
    x = int(flask.request.args["x"])
    y = int(flask.request.args["y"])
    annotation = flask.request.args["annotation"]

    photo.annotate_labels(source, annotation, x, y)

    return '',HTTPStatus.NO_CONTENT
