from http import HTTPStatus

import numpy as np

from btviewer.blueprints.photo.model import Photo

PHOTO_PATH = '2020-01-01/set_A/device_1/camera_1/20200101_094359.123456_000001.np'


def test_photo_array(app_context):
    photo = Photo(PHOTO_PATH)

    assert isinstance(photo.array, np.ndarray)
    assert photo.array.shape == (1536, 2048)
    assert photo.array.min() >= 0
    assert photo.array.max() <= 255


def test_photo_jpeg(client):
    width = 1024
    height = 768
    response = client.get('photos/2020-01-01/set_A/device_1/camera_1/20200101_094359.123456_000001.jpeg')
    assert response.status_code == HTTPStatus.OK

    # Check response contents
    assert response.content_type == 'image/jpeg'

    # TODO check dimensions
    # import PIL.Image
    # PIL.Image.frombytes(mode='L', size=(width, height), dataresponse.data)


def test_select_region_of_interest(app_context):
    photo = Photo(PHOTO_PATH)

    # Define region of interest
    x0 = 10
    y0 = x0 + 10
    box = ((x0, x0), (y0, y0))

    region_of_interest = photo.select_region_of_interest(box)

    assert isinstance(region_of_interest, np.ndarray)
    assert region_of_interest.shape == (y0 - x0, y0 - x0)


def test_find_brightest_pixel(app_context):
    photo = Photo(PHOTO_PATH)

    # Define region of interest
    x0 = 10
    y0 = x0 + 10
    box = ((x0, x0), (y0, y0))

    # Run the code
    x, y = photo.find_brightest_pixel(box=box)

    # Check data type
    assert isinstance(x, int)
    assert isinstance(y, int)

    # Check pixel position
    assert x0 <= x <= y0
    assert x0 <= y <= y0
